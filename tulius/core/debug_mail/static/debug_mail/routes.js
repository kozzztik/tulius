import users from './users.js'
import mailbox from './mailbox.js'
import mail from './mail.js'


export default [
    {path: '/debug_mail/', component: users, name: 'debug_mail_users'},
    {path: '/debug_mail/:email([^\/]+)/', component: mailbox, name: 'debug_mail_box'},
    {path: '/debug_mail/:email([^\/]+)/:pk([^\/]+)', component: mail, name: 'debug_mail_text'},


]
