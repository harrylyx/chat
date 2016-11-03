/**
 * Created by Slane on 2016/10/16.
 */
var address = 'ws://127.0.0.1:7000/soc';
var ws = new WebSocket(address);
ws.onmessage = function(event) {
    var content;
    var data =  JSON.parse(event.data);
    var container = $('#J_message');
    console.log("收到数据："+data);

    if(data.type == 'sys'){
        content = '<p class="system-msg">'+ data.message + '</p>';
        container.append(content);
    } else if (data.type == 'user') {
        content =   '<p class="user-msg">'+
                        '<img class="user-img" src="../static/images/user.jpg" alt="头像">'+
                        '<span class="user-name">' + data.name + '</span>'+
                        '<span class="user-time">' + data.time + '</span>'+
                        '<div class="user-message">' + data.message + '</div>'+
                    '</p>'
        container.append(content);
    }
    //滚动到底部
    $('#J_message').animate({
        scrollTop: $('#J_message').height()
    },500);

    // //转化为标准时间函数
    // function getLocalTime(time) {
    //     var date = new Date(time);
    //     Y = date.getFullYear() + '-';
    //     M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '-';
    //     D = date.getDate() + ' ';
    //     h = date.getHours() + ':';
    //     m = date.getMinutes() + ':';
    //     s = date.getSeconds(); 
    //     return Y+M+D+h+m+s
    // }
};

$('#J_send').on('click touch', function() {
    var ele = document.getElementById('chat');
    if (ele.value) {
        ws.send(ele.value);
        console.log("发送数据："+ele.value);
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
