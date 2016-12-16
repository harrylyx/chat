/**
 * Created by Slane on 2016/10/16.
 */
var address = 'wss://chat.crazyc.cn/soc';
var ws = new WebSocket(address);
ws.onmessage = function(event) {
    var content;
    var data =  JSON.parse(event.data);
    var container = $('#J_message');
    // console.log(data);

    if(data.type == 'sys'){
        content = '<div><p class="system-msg">'+ data.message + '</p></div>';
        container.append(content);
        $("#J-person").html(data.person);
    } else if (data.type == 'user') {
        if (data.itisme == 1) {
            content =   '<div><p class="user-time">'+ data.time + '</p></div>'+
                        '<div class="user-msg user-me-msg">'+
                            '<img class="user-img user-me-img" src="../static/images/otherUser.jpg" alt="头像">'+
                            '<span class="user-name user-me-name">' + data.name + '</span>'+
                            '<div class="user-message user-me-message">' + data.message + '</div>'+
                        '</div>'
        } else {
            content =   '<div><p class="user-time">'+ data.time + '</p></div>'+
                        '<div class="user-msg">'+
                            '<img class="user-img" src="../static/images/user.jpg" alt="头像">'+
                            '<span class="user-name">' + data.name + '</span>'+
                            '<div class="user-message">' + data.message + '</div>'+
                        '</div>'
        }
        container.append(content);
    } else if (data.type == 'bot') {
        //机器人
        content =   '<div><p class="user-time">'+ data.time + '</p></div>'+
            '<div class="user-msg">'+
            '<img class="user-img" style="border-radius: 50%" src="../static/images/robot.png" alt="头像">'+
            '<span class="user-name">' + data.name + '</span>'+
            '<div class="user-message user-robot-msg">' + data.message + '</div>'+
            '</div>'
        container.append(content);
    }
    //滚动到底部
    var container = $('#J_message'),
        scrollTo = $('#J_message div:last');
    container.animate({
        scrollTop: scrollTo.offset().top - container.offset().top + container.scrollTop()
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

ws.onopen = function (event) {
    //第一次连接  启动心跳包
    keepOnline();
}

function keepOnline() {
    // 心跳包函数，每30秒 呼叫一次服务器
    setInterval(function () {
        ws.send('c93c60882b37254bb13e80183f291af3');
    },30000)
}

$('#J_send').on('click touch', function() {
    var ele = document.getElementById('chat');
    // var safeVal = filterXSS(ele.value);
    var safeVal = ele.value;
    if (safeVal) {
        //发送前过滤XSS
        //发送
        ws.send(safeVal);
        // console.log("发送数据："+ele.value);
        // 清空数据，重置高度
        ele.value = '';
        ele.style.height = "50px";
    } else {
        // alert("内容非法！");
        // console.log("nothing");
    }
});
document.onkeydown=function() {
    //绑定回车键+ctrl键
    var e = event || window.event;
    if (e.keyCode == 13 &&  e.ctrlKey) {
        $('#J_send').trigger('click');
    };
    // if (e.keyCode == 13) {
    //     //回车键 触发发送按钮
    //     $('#J_send').trigger('click');
    // };

};
