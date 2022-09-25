document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});


function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#view-email').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  // When click Send, sends the email 
  document.querySelector("#compose-form")[4].addEventListener('click', send_email);
}


async function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#view-email').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Fetch GET request
  const response = await fetch(`/emails/${mailbox}`);
  const emails = await response.json();

  // Render the page
  render_page(mailbox, emails);
}


async function render_page(mailbox, emails){
  for (let email of emails){
    const emailsViewChild = document.createElement('div');
    const newDiv = document.createElement('div');
    const senderDiv = document.createElement('div');
    const subjectDiv = document.createElement('div');
    const timestampDiv = document.createElement('div');

    senderDiv.innerHTML = `${email.sender}`;
    subjectDiv.innerHTML = `${email.subject}`;
    timestampDiv.innerHTML = `${email.timestamp}`;
    newDiv.className = 'email-view';
    senderDiv.id = 'sender-view';
    subjectDiv.id = 'subject-view';
    timestampDiv.id = 'timestamp-view';
    emailsViewChild.id = 'emails-view-child';

    newDiv.appendChild(senderDiv);
    newDiv.appendChild(subjectDiv);
    newDiv.appendChild(timestampDiv);

    // Change color to div if read
    if (email.read == true) newDiv.style.backgroundColor = "grey";

    // Add event listeners
    newDiv.addEventListener('mouseover', () => {newDiv.style.cursor = 'pointer'});
    newDiv.addEventListener('click', () => view_email(`${email.id}`));

    // Append div
    emailsViewChild.appendChild(newDiv)
    
    // Add Archive / Unarchive button
    if (mailbox != 'sent') add_archive_btn(email, emailsViewChild)
    
    // Appends all
    document.querySelector('#emails-view').appendChild(emailsViewChild);
  }
}


async function add_archive_btn(email, parent){

  const archBtn = document.createElement('input');
      archBtn.type = 'button';
      archBtn.id = 'arch-btn';
      archBtn.className ='btn btn-primary';
      if (email.archived) archBtn.value ='Unarchive';
      else archBtn.value ='Archive';

      archBtn.addEventListener('click', async () => {

        //PUT and update 
        await fetch(`/emails/${email.id}`, {
          method: 'PUT',
          body: JSON.stringify({
            "archived": !email.archived
          })
        });

        // Load mailbox
        await load_mailbox('inbox');
      })

      // Append button
      parent.appendChild(archBtn)
}


async function view_email(id) {

  // Show compose view and hide other views
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#view-email').style.display = 'block';

  // Fetch PUT request
  await fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
      "read": true
    })
    });
  
  // Fetch GET request
  const viewData = await fetch(`/emails/${id}`);
  const email = await viewData.json();

  // Render the page
    document.querySelector('#view-sender').innerHTML = email.sender;
    document.querySelector('#view-subject').innerHTML = email.subject;
    document.querySelector('#view-timestamp').innerHTML = email.timestamp;
    document.querySelector('#view-body').innerHTML = email.body;
    for (let recipient in email.recipients){
      document.querySelector('#view-recipients').innerHTML = email.recipients[recipient];
    }
  
  // Add event listener to the button
  document.querySelector('#reply').addEventListener('click', () => reply_email(`${email.id}`)); 
  //nueva funcion reply email donde se pregargan los values y luego se usa sendemail(aaaaaa)
}


async function send_email() {

  const request = {
    method: 'POST',
    body: JSON.stringify({
      "recipients": document.querySelector('#compose-recipients').value,
      "subject": document.querySelector('#compose-subject').value,
      "body": document.querySelector('#compose-body').value
    })
  };

  // Fetch POST request
  const response = await fetch('/emails', request); 
  const result = await response.json();
  console.info(result);

  // Redirects to 'sent' mailbox
  load_mailbox('sent'); 
}


async function reply_email(id){

  // Show compose view and hide other views
  document.querySelector('#view-email').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Fetch GET request
  const replyData = await fetch(`/emails/${id}`);
  const reply = await replyData.json();

  console.log(reply)
  console.log(reply.recipient)
  console.log(reply.subject)
  console.log(reply.body)

  // Pre-fill composition
  if ("Re:" === reply.subject.substring(0,3)) document.querySelector('#compose-subject').value = reply.subject;
  else document.querySelector('#compose-subject').value = `Re: ${reply.subject}`;
  document.querySelector('#compose-body').value = `On ${reply.timestamp} ${reply.sender} wrote:\n${reply.body}`;
  document.querySelector('#compose-recipients').value = reply.sender;

  // When click Reply, sends the email 
  document.querySelector("#compose-form")[4].addEventListener('click', send_email)
}