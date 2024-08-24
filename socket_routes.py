from flask_socketio import emit
from flask import json, request, session

import dateutil.parser
try:
    from __main__ import socketio
except ImportError:
    from app import socketio

import db
import html

user_sessions = {}
user_rooms = {}
public_key_events = {}

def get_user_session_id(username):
    """Retrieve the session ID for a given username."""
    return user_sessions.get(username)


@socketio.on('send_friend_request')
def handle_send_friend_request(data):
    user_username = data['username']
    friend_username = data['friendUsername']

    if user_username == friend_username:
        emit('friend_request_response', {'success': False, 'message': "You can't add yourself as a friend"}, to=request.sid)
        return

    result = db.create_friend_request(user_username, friend_username)
    friend_obj = db.get_user_by_username(friend_username)
    
    if friend_obj not in db.get_friend_list(user_username):
        if result[0] == 0:
            request_id = result[1]
            emit('friend_request_response', {'success': True, 'message': 'Friend request sent successfully'}, to=request.sid)
            
            friend_sid = get_user_session_id(friend_username)
            updates = []
            if friend_sid:
                emit('new_friend_request',{
                    'sender': user_username,
                    'id': request_id
                }, to=friend_sid)
            else:
                updates.append({
                    "username": friend_username, 
                    "update_type": "new_friend_request", 
                    "details": json.dumps({"sender": user_username, "id": request_id, "flag": result[2]})
                })
                
            if updates:
                db.create_pending_updates(updates)
        elif result[0] == 1:
            emit('friend_request_response', {'success': False, 'message': 'Friend request already sent'}, to=request.sid)
        elif result[0] == -1:
            emit('friend_request_response', {'success': False, 'message': 'User does not exist'}, to=request.sid)
        else:
            emit('friend_request_response', {'success': False, 'message': 'Failed to send friend request'}, to=request.sid)
    else:
        emit('friend_request_response', {'success': False, 'message': 'User is already your friend'}, to=request.sid)
  
@socketio.on('accept_friend_request')
def handle_accept_friend_request(data):
    if 'request_id' not in data:
        emit('friend_request_answer', {'success': False, 'message': 'Missing request ID', 'requestId': None})
        return

    result = db.accept_friend_request_with_details(data['request_id'])
    if result["success"]:
        updates = []
        sender_sid = get_user_session_id(result["sender_name"])
        receiver_sid = get_user_session_id(result["receiver_name"])
        
        if sender_sid:
            emit('friend_request_accepted', {
                'username': result["receiver_name"],
                'status': result["receiver_status"],
                'role': result["receiver_role"]
            }, to=sender_sid)
        else:
            # Create pending update for sender
            updates.append({
                "username": result["sender_name"], 
                "update_type": "friend_added", 
                "details": json.dumps({
                    "username": result["receiver_name"],
                    "status": result["receiver_status"],
                    'role': result["receiver_role"]
                })
            })
            
        if receiver_sid:
            emit('friend_request_accepted', {
                'username': result["sender_name"],
                'status': result['sender_status'],
                'role': result["sender_role"]
            }, to=receiver_sid)
        else:
            # Create pending update for receiver
            updates.append({
                "user_id": result["receiver_name"], 
                "update_type": "friend_added", 
                "details": json.dumps({
                    "username": result["sender_name"],
                    "status": result["sender_status"],
                    'role': result["sender_role"]})
            })
        
        if updates:
            db.create_pending_updates(updates)
            
        emit('friend_request_answer', {'success': True, 'message': 'Friend request accepted', 'requestId': data['request_id']})
    else:
        emit('friend_request_answer', {'success': False, 'message': 'Unable to accept friend request', 'requestId': data['request_id']})

@socketio.on('decline_friend_request')
def handle_decline_friend_request(data):
    if 'request_id' not in data:
        emit('friend_request_answer', {'success': False, 'message': 'Missing request ID', 'requestId': None})
        return

    result = db.decline_friend_request(data['request_id'])
    if result:
        emit('friend_request_answer', {'success': True, 'message': 'Friend request declined', 'requestId': data['request_id']})
        emit('friend_request_resolved', {'requestId': data['request_id']}, to=request.sid)
    else:
        emit('friend_request_answer', {'success': False, 'message': 'Unable to decline friend request', 'requestId': data['request_id']})

def update_friend_list(username, status):
    """ Update the friend list for a user in real-time """
    user_sid = get_user_session_id(username)
    if user_sid:
        emit('update_friend_list', {
            'username': username,
            'status': status
        }, room=user_sid)
