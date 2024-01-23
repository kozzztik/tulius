jQuery(document).ready(function($) {
    const evtSource = new EventSource("/api/ws/sse/");
    evtSource.addEventListener("pm", (event) => {
        const content = JSON.parse(event.data)
        if (content['.action'] == 'new_pm') {
            $('.new_messages').addClass('active');
            $('.new_messages').attr('title', "У вас новое сообщение!")
        }
    });
});
