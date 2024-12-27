document.addEventListener('DOMContentLoaded', function () {
    var button = document.getElementById('like-button');
    button.addEventListener('click', function () {
        var url = button.getAttribute('data-url');
        console.log(url);
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token() }}'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // update the likes count
                    document.getElementById('likes-count').innerText = data.likes_count;

                    // update the button text
                    button.innerHTML = data.liked ? '<i class="bi bi-heart-fill"></i> Unlike' : '<i class="bi bi-heart"></i> Like';

                    // make sure the button has the correct URL
                    button.setAttribute('data-url', data.new_url);  // 如果你需要动态更新 URL 可以这样处理
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => console.error('Error:', error));
    });
});
