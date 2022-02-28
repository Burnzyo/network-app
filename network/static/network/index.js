function post() {
    post = document.querySelector("#post_content").value
    fetch('/newpost', {
        method: 'POST',
        body: JSON.stringify({
            post: post
        })
      })
        .then(response => response.json())
        .then(result => {
            // Print result
            console.log(result);
            result.error ? alert(`ERROR: ${result.error}`) : alert(`SUCCESS: ${result.message}`);
            document.location.reload();
        });
}

function follow() {
    const button = document.querySelector(".follow_button");
    const username = document.querySelector("#profile_username").textContent.toLowerCase();
    if (button.textContent === "Follow") {
        fetch("/follow", {
            method: "POST",
            body: JSON.stringify({
                following: username
            })
        })
        .then(response => response.json())
        .then(result => {
            //Print result.
            console.log(result);
            document.location.reload();
        });
    }
    else if (button.textContent === "Unfollow") {
        fetch("/unfollow", {
            method: "POST",
            body: JSON.stringify({
                following: username
            })
        })
        .then(response => response.json())
        .then(result => {
            //Print result.
            console.log(result);
            document.location.reload();
        });
    }
}

function edit_post(id) {
    const post = document.getElementById(id);
    const div = post.parentNode;
    const text_area = document.createElement('textarea');
    const button = document.createElement('button');
    const br = document.createElement('br');

    post.hidden = true;
    div.childNodes[3].hidden = true;
    
    text_area.classList.add("form-control");
    text_area.innerHTML = post.textContent.trim();
    div.childNodes[3].after(text_area);
    
    button.classList.add("btn", "btn-primary");
    button.onclick = () => {
        post.hidden = false;
        div.childNodes[3].hidden = false;
        div.removeChild(text_area);
        div.removeChild(button);
        div.removeChild(br);
        fetch(`/update/${id}`, {
            method: 'PUT',
            body: JSON.stringify({
                post: text_area.value
            })
        })
        .then(response => response.json())
        .then(result => {
            console.log(result);
            result.error ? alert(`ERROR: ${result.error}`) : post.textContent = text_area.value;
        });
    }
    button.innerHTML = "Save";
    div.append(br);
    div.append(button);
}

function like(id) {
    const like_button = document.getElementById(`like_${id}`);
    const dislike_button = document.getElementById(`dislike_${id}`);
    const like_count = document.getElementById(`like_count_${id}`);

    if (like_button != null) {
        var new_dislike_button = document.createElement("i");
        new_dislike_button.id = `dislike_${id}`;
        new_dislike_button.classList.add("bi", "bi-heart-fill");
        new_dislike_button.addEventListener("click", () => like(id));
        like_button.after(new_dislike_button);
        like_button.parentNode.removeChild(like_button);
        like_count.innerHTML++;
        fetch(`/like/${id}`, {
            method: 'PUT',
            body: JSON.stringify({
                like: true
            })
        })
        .then(response => response.json())
        .then(result => {
            console.log(result);
        });
    }
    else if (dislike_button != null) {
        var new_like_button = document.createElement("i");
        new_like_button.id = `like_${id}`;
        new_like_button.classList.add("bi", "bi-heart");
        new_like_button.addEventListener("click", () => like(id));
        dislike_button.after(new_like_button);
        dislike_button.parentNode.removeChild(dislike_button);
        like_count.innerHTML--;
        fetch(`/like/${id}`, {
            method: 'PUT',
            body: JSON.stringify({
                like: false
            })
        })
        .then(response => response.json())
        .then(result => {
            console.log(result);
        });
    }
}