/**
 * Created by Slane on 2016/10/16.
 */
var address = 'ws://127.0.0.1:7000/soc';
var ws = new WebSocket(address);
ws.onmessage = function(event) {
    var content;
    var data =  JSON.parse(event.data);
    var container = $('#J_message');
    console.log(data);

    if(data.type == 'sys'){
        content = "<p>" + data.message + "</p>";
        container.append(content);
    } else if (data.type == 'user') {
        content = "<p>" + data.message + "</p><p>" + data.name + "</p>" + "<span>" + data.time + "</span>";
        container.append(content);
    }

};

$('#J_send').on('click touch', function() {
    var ele = document.getElementById('chat');
    if (ele.value) {
        ws.send(ele.value);
        ele.value = '';
    } else {
        console.log("nothing");
    }
});
document.onkeydown=function() {
    //绑定回车键
    var e = event || window.event;
    if (e.keyCode == 13) {
        $('#J_send').trigger('click');
    };

};
