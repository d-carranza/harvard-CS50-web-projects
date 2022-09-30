document.addEventListener('DOMContentLoaded', async function() {

  // Make sure hidden stuff is hidden
  const hiddenrows = document.querySelectorAll('.hidden');
  for (row of hiddenrows){
    row.style.display = 'none';
  }

  // Get loged user and poster
  const user = document.querySelector('#username').innerHTML;
  const poster = document.querySelector('#postername').innerHTML;

  // Add follow/unfollow button
  if (user != poster) add_follow_btn(user, poster);
});


async function add_follow_btn(user, poster){
  const followBtn = document.createElement('input');
    followBtn.type = 'button';
    followBtn.id = 'follow-btn';
    followBtn.className ='btn btn-primary';

  // Is follower or is not follower?
  const response = await fetch(`/follow`, {
    method: 'POST',
    body: JSON.stringify({
      "user": user,
      "poster": poster
    })
  });
  const result = await response.json();
  const isfollower = result["isfollower"];
  
  if (isfollower) followBtn.value = 'Unfollow';
  else followBtn.value = 'Follow';

  // Update value when clicked
  followBtn.addEventListener('click', async () => {
    await fetch(`/follow`, {
      method: 'PUT',
      body: JSON.stringify({
        "user": user,
        "poster": poster
      })
    });
    window.location.reload()
  })

  // Append button
  document.querySelector('#followbtn').appendChild(followBtn)
}
  

function editclick(id){

  document.querySelector(`#post-${id}`).style.display = 'none';
  document.querySelector(`#edit-${id}`).style.display = 'block';
  const text = document.querySelector(`#text-${id}`).innerText
  const textdiv = document.querySelector(`#edit-${id}`)
  const textarea = textdiv.querySelector("textarea")
  textarea.value = text.trim()
}


async function saveedit(id){

  const textdiv = document.querySelector(`#edit-${id}`)
  const textarea = textdiv.querySelector("textarea")
  const text =  textarea.value
  console.log(text)
  console.log('here ok')

  // Fetch post to the server
  const response = await fetch(`/edit`, {
    method: 'POST',
    body: JSON.stringify({
      "id": id,
      "text": text
    })
  });
  const result = await response.json();
  console.log(result)

  // Update results in the div
  document.querySelector(`#post-${id}`).style.display = 'block';
  const newpost = document.querySelector(`#text-${id}`)
  newpost.innerHTML = text
  document.querySelector(`#edit-${id}`).style.display = 'none';
}


async function like(id){
  const user = document.querySelector('#username').innerHTML;
  const likediv = document.getElementById(`${id}-like`)
  const name = likediv.querySelector('button').innerText

  console.log(name)

   // Update value
  await fetch(`/like`, {
    method: 'POST',
    body: JSON.stringify({
      "id": id,
      "user": user
    })
  });
  
  // Change visibility
  if (document.getElementById(`${id}-unlike`).style.display != 'none'){
    document.getElementById(`${id}-like`).style.display = 'block';
    document.getElementById(`${id}-unlike`).style.display = 'none';
  }
  else if (document.getElementById(`${id}-unlike`).style.display = 'none'){
    document.getElementById(`${id}-like`).style.display = 'none';
    document.getElementById(`${id}-unlike`).style.display = 'block';
  }
 
  // Update counter
  let counter = document.getElementById(`like-${id}-count`).innerHTML
  counter++
  document.getElementById(`like-${id}-count`).innerHTML = counter
}


async function unlike(id){
  const user = document.querySelector('#username').innerHTML;

  // Update value 
  await fetch(`/unlike`, {
    method: 'POST',
    body: JSON.stringify({
      "id": id,
      "user": user
    })
  });


  // Change visibility
  if (document.getElementById(`${id}-like`).style.display != 'none'){

    document.getElementById(`${id}-like`).style.display = 'none';
    document.getElementById(`${id}-unlike`).style.display = 'block';
  }
  else if (document.getElementById(`${id}-like`).style.display = 'none'){
    document.getElementById(`${id}-like`).style.display = 'block';
    document.getElementById(`${id}-unlike`).style.display = 'none';
  }

  // Update counter
  let counter = document.getElementById(`like-${id}-count`).innerHTML
  counter--
  document.getElementById(`like-${id}-count`).innerHTML = counter
}
