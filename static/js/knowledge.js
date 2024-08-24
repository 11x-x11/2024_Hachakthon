function createArticle() {
    const articleEl = document.getElementById('make_article');
    const articleTitleEl = document.getElementById('article_title');
    const data = {
        content: articleEl.value.toString(),
        title: articleTitleEl.value.toString()
    };
    if (!articleTitleEl.value) {
        alert('Please fill article title');
        return;
    }
    if (!articleEl.value) {
        alert('Please fill article content');
        return;
    }
}

function toggleEditMode(articleId) {
    const titleEl = document.getElementById('article_title_' + articleId);
    const contentEl = document.getElementById('article_content_' + articleId);
    const modifyButton = document.getElementById('modify_button_' + articleId);

    if (modifyButton.innerText === 'Modify') {
        // Enable editing
        titleEl.removeAttribute('readonly');
        contentEl.removeAttribute('readonly');
        modifyButton.innerText = 'Save';
    } else {
        // Save changes
        modifyArticle(articleId);
        // Disable editing
        titleEl.setAttribute('readonly', 'readonly');
        contentEl.setAttribute('readonly', 'readonly');
        modifyButton.innerText = 'Modify';
    }
}

function modifyArticle(articleId) {
    const title = document.getElementById('article_title_' + articleId).value.trim();
    const content = document.getElementById('article_content_' + articleId).value.trim();
    if (!title) {
        alert('Article title cannot be empty');
        return;
    }
    if (!content) {
        alert('Article content cannot be empty');
        return;
    }
    const data = {
        id: articleId,
        title: title,
        content: content
    };
    socket.emit('modify_article', data);
}

function deleteArticle(articleId) {
    socket.emit('delete_article', { id: articleId });
}

function addComment(articleId) {
    const val = document.getElementById('make_comment_' + articleId).value.trim();
    if (!val) {
        alert('Comment cannot be empty');
        return;
    }
    const data = {
        id: articleId,
        content: val
    };
    socket.emit('create_comment', data);
    clearCommentInputBoxes(`make_comment_${articleId}`);
}

function deleteComment(articleId, commentId) {
    socket.emit('delete_comment', { article_id: articleId, id: commentId });
}


function clearInputBoxes() {
    document.getElementById('article_title').value = '';
    document.getElementById('make_article').value = '';
}

function appendArticle(article) {
    const articlesContainer = document.getElementById('articles');
    const articleElement = document.createElement('div');
    articleElement.className = 'article';
    articleElement.id = `article_${article.article_id}`;

    const staffRoles = ['admin', 'academics', 'administrative'];
    const currentUserRole = document.getElementById('current_user_role').value;
    const currentUsername = document.getElementById('currentUsername').value;
    const isStaff = staffRoles.includes(currentUserRole);

    const canModify = isStaff || article.can_modify;
    const canDelete = isStaff || article.can_delete;

    const isLiked = article.liked_by.includes(currentUsername);

    articleElement.innerHTML = `
        <div class="flex-row">
            <input class="article-setting" value="${article.title}"
                   id="article_title_${article.article_id}" readonly/>
            <h4>by ${article.author} (${article.author_role})</h4>
        </div>
        <textarea class="article-setting"
                  id="article_content_${article.article_id}" readonly>${article.content}</textarea>
        <div class="flex-row">
            <a class="heart ${isLiked ? 'liked' : ''}" href="#" onclick="switchArticleLike('${article.article_id}', '${currentUsername}')"></a>
            <span class="margin-4">${article.liked_count}</span>
            ${canModify ? `<button id="modify_button_${article.article_id}" onclick="toggleEditMode('${article.article_id}')" class="button margin-4">Modify</button>` : ''}
            ${canDelete ? `<button onclick="deleteArticle('${article.article_id}')" class="button margin-4">Delete</button>` : ''}
        </div>
        <div class="comments">
            <h4>Comments</h4>
            <ul id="comment_list_${article.article_id}">
                ${(Array.isArray(article.comments) ? article.comments : []).map(comment => `
                    <li id="comment_${comment.id}">
                        ${comment.author} (${comment.author_role}): ${comment.content}
                        ${isStaff ? `<button onclick="deleteComment('${article.article_id}', '${comment.id}')" class="button">Delete</button>` : ''}
                    </li>
                `).join('')}
            </ul>
            <input type="text" placeholder="Add a comment" class="input-box" id="make_comment_${article.article_id}">
            <button onclick="addComment('${article.article_id}')" class="button">Add Comment</button>
        </div>
    `;
    articlesContainer.appendChild(articleElement);
    clearInputBoxes();
}

function updateArticleInDOM(article) {
    const articleElement = document.getElementById(`article_${article.article_id}`);
    if (articleElement) {
        const titleEl = articleElement.querySelector(`#article_title_${article.article_id}`);
        const contentEl = articleElement.querySelector(`#article_content_${article.article_id}`);
        titleEl.value = article.title;
        contentEl.value = article.content;
    }
}

function removeArticleFromDOM(article) {
    const articleElement = document.getElementById(`article_${article.article_id}`);
    if (articleElement) {
        articleElement.remove();
    }
}

function clearCommentInputBoxes(commentInputId) {
    if (commentInputId) {
        document.getElementById(commentInputId).value = '';
    }
}

function appendComment(comment) {
    const commentList = document.getElementById(`comment_list_${comment.article_id}`);
    if (commentList) {
        const commentElement = document.createElement('li');
        commentElement.id = `comment_${comment.comment_id}`;

        const staffRoles = ['admin', 'academics', 'administrative'];
        const currentUserRole = document.getElementById('current_user_role').value;
        const isStaff = staffRoles.includes(currentUserRole);

        commentElement.innerHTML = `
            ${comment.author}(${comment.author_role}): ${comment.content}
            ${isStaff ? `<button onclick="deleteComment('${comment.article_id}', '${comment.comment_id}')" class="button">Delete</button>` : ''}
        `;
        commentList.appendChild(commentElement);

    }
}

function updateCommentInDOM(comment) {
    const commentElement = document.getElementById(`comment_${comment.comment_id}`);
    if (commentElement) {
        // Update the content inside the comment element

        const staffRoles = ['admin', 'academics', 'administrative'];
        const currentUserRole = document.getElementById('current_user_role').value;
        const isStaff = staffRoles.includes(currentUserRole);
        
        commentElement.innerHTML = `
            ${comment.author}(${comment.author_role}): ${comment.content}
            ${isStaff ? `<button onclick="deleteComment('${comment.article_id}', '${comment.comment_id}')" class="button">Delete</button>` : ''}
        `;
    }
}

function removeCommentFromDOM(articleId, commentId) {
    const commentList = document.getElementById(`comment_list_${articleId}`);
    if (commentList) {
        const comments = commentList.getElementsByTagName('li');
        for (let i = 0; i < comments.length; i++) {
            const commentElement = comments[i];
            if (commentElement.id === `comment_${commentId}`) {
                commentElement.remove();
                break;
            }
        }
    }
}
