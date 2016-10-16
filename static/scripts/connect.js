/**
 * Created by Slane on 2016/10/16.
 */
var address = 'ws://172.18.61.245:8000/soc';
var ws = new WebSocket(address);
ws.onmessage = function(event) {
    console.log(event.data);
    var table = document.getElementById('message');
    var data = eval('(' + event.data + ')');
    ({
        'sys': function() {
            var cell = table.insertRow().insertCell();
            cell.colSpan = 2;
            cell.innerHTML = data['message'];
        },
        'user': function() {
            var row = table.insertRow();
            row.insertCell().innerHTML = data['message'];
            row.insertCell().innerHTML = data['id'];
        },
    }[data['type']])();
};
function send() {
    ws.send(document.getElementById('chat').value);
    document.getElementById('chat').value = '';
}