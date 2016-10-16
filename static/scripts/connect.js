/**
 * Created by Slane on 2016/10/16.
 */
var address = 'ws://113.251.161.191:8000/soc';
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
        content = "<p>" + data.message + "</p><p>" + data.name + "</p>" + "<span>" + data.name + "</span>";
        container.append(content);
    }
    // ({
    //     'sys': function() {
    //         var cell = table.insertRow().insertCell();
    //         cell.colSpan = 2;
    //         cell.innerHTML = data['message'];
    //     },
    //     'user': function() {
    //         var row = table.insertRow();
    //         row.insertCell().innerHTML = data['message'];
    //         row.insertCell().innerHTML = data['id'];
    //     },
    // }[data['type']])();
};
$('#J_send').on('click touch', function () {
    ws.send(document.getElementById('chat').value);
    document.getElementById('chat').value = '';
})
