     var ws = new WebSocket("ws://localhost:8000/ws");
      ws.onmessage = function (event) {
        var messages = document.getElementById("messages");
        var message = document.createElement("li");
        var content = document.createTextNode(event.data); //정보 가져 오는 것
        // message.appendChild(content);
        // messages.appendChild(message);
      };
      $(document).ready(function () {

        var urlParts = getClientIdFromUrl();
        var friend_name = decodeURIComponent(urlParts[urlParts.length - 1]);
        var room_type= decodeURIComponent(urlParts[urlParts.length - 2]);
        $("#friend_name").text(friend_name);//그룹 제목이자 친구 이름
        // <ul id="members"></ul>여기에 append 해줘야함
        var usern;
        $.getJSON("/getuser",function(user){//모든 유저 정보임
          var isGroup=0;
          user.forEach((item) => {//item은 유저 한명의 정보
            array=item.friends;
            searchString=friend_name;
            if (array.includes(searchString)) {
                console.log(item);
                console.log(searchString + "이(가) 배열에 존재합니다.");
                var li1='<li class="member">'+item.name+'</li>';
                $("#members").append(li1);  
                isGroup++;
            } else {
                console.log(searchString + "이(가) 배열에 존재하지 않습니다.");
            }
          });
        });
        console.log(friend_name);
        var user_name;
        $.getJSON("/current_user",function(user){
          user_name=user;
          console.log(user_name);
          $("#client_name").text(user_name);
          $("#chat-content").empty();
          $.getJSON("/getchat",function(chatcontent){
            chatcontent.forEach((item) => {
              // console.log(item.receiver_name);
              
              if(room_type=="groupchat"){
                  if(user_name==item.sender_name && friend_name==item.receiver_name){
                    // alert("same");
                    var to_div1 = item.in_sender_message;
                    $("#chat-content").append(to_div1);
                  }
                  else if(friend_name==item.receiver_name){
                    var to_div2 = item.in_receiver_message;
                    $("#chat-content").append(to_div2);
                  }
              }
              else if(room_type=="friendchat"){
                  if(user_name==item.sender_name && friend_name==item.receiver_name){
                    // alert("same");
                    var to_div1 = item.in_sender_message;
                    $("#chat-content").append(to_div1);
                  }
                  else if(user_name==item.receiver_name && friend_name==item.sender_name){
                    var to_div2 = item.in_receiver_message;
                    $("#chat-content").append(to_div2);
                  }
              }

            });
            $('#chat-content').scrollTop($('#chat-content')[0].scrollHeight);
          });
        });
      $(function(){
                $("#popup_btn1").click(function(){
                  sendImage();
                  console.log("click");
                  var image=$("#send_image").val();
                  console.log(image);
                  modalClose1(); //모달 닫기 함수 호출
                    
                    //컨펌 이벤트 처리
                });
                $("#photo_btn").click(function(){        
                    $("#popup").css('display','flex').hide().fadeIn();
                    //팝업을 flex속성으로 바꿔준 후 hide()로 숨기고 다시 fadeIn()으로 효과
                });
                $("#popup_btn2").click(function(){
                    modalClose2(); //모달 닫기 함수 호출
                });
                function modalClose1(){
                    $("#popup").fadeOut(); //페이드아웃 효과
                    $("#popup_friend_name").val(''); //input 초기화
                }
                function modalClose2(){
                    $("#popup").fadeOut(); //페이드아웃 효과
                    $("#popup_friend_name").val(''); //input 초기화
                }
                function sendImage(){
                    $("#textarea1").focus();
                    var now = new Date();
                    var hour = now.getHours();
                    var num_minute = now.getMinutes();
                    var str_minute=num_minute.toString();
                    var image = $('#send_image').val();

                    if(image){
                       var input = document.getElementById('send_image');
                       var file = input.files[0];
                       var reader = new FileReader();
                       reader.onload = function (e) {
                        // 이미지를 Base64로 인코딩
                        var imageData = e.target.result;
                        console.log(imageData);
                          // 전송할 JSON 데이터 생성
                        if (num_minute < 10) str_minute = "0" + str_minute;
                        if (hour >= 12) {
                            var half = "오후";
                            hour -= 12;
                        }
                        else {
                            var half = "오전";
                        }
                        if(hour==0){
                          hour=12;
                        }
                        let to_div1 = '<div class="user_chat"> <div class="user_time">' + half + " " + hour + " : " + str_minute + '</div>  <div class="yellow"><img class="send_img" src="' + imageData + '"style="max-width: 150px; max-height: 150px;" onclick="click_img(this)"/></div> </div>';
                        // $("#chat-content").append(to_div1);
                        let c_id=$("#client_name").text();
                        console.log(c_id);
                        let f_id=$("#friend_name").text();
                        console.log(f_id);
                        let to_div2= '<div class=friend_wrapper><div class="friend_name">'+c_id+'</div><div class="friend_chat"> <div class="white"><img class="send_img" src="' + imageData + '"style="max-width: 150px; max-height: 150px;" onclick="click_img(this)"/></div>  <div class="friend_time">' + half + " " + hour + " : " + str_minute + '</div> </div></div>';
                        ws.send(JSON.stringify({"write_client":c_id, "text":imageData}));
                        // $("#chat-container2").append(to_div2);
                        $('#textarea1').val('');
                        $('#chat-content').scrollTop($('#chat-content')[0].scrollHeight);
                        // $('#chat-container2').scrollTop($('#chat-container2')[0].scrollHeight);
                        var data={"sender_name":c_id,"receiver_name":f_id, "in_sender_message":to_div1,"in_receiver_message":to_div2,"photo_data":imageData};
                        $.ajax({
                          url:"/postchat",
                          type:"post",
                          contentType:"application/json",
                          dataType:"json",
                          data:JSON.stringify(data),
                          success:function(chat){
                            console.log(chat);
                          }           
                        });
                    }
                    reader.readAsDataURL(file);
                    event.preventDefault();
                            
                    $('#send_image').val('');}
                  }
            });
            $(function(){
                $("#popup_btn_close").click(function(){
                  console.log("click");
                  modalClose1(); //모달 닫기 함수 호출
                    
                    //컨펌 이벤트 처리
                });
                function modalClose1(){
                    $("#popup_img").fadeOut(); //페이드아웃 효과
                }
            });   
            

      });
      function click_img(img){
          $("#popup_img").css('display','flex').hide().fadeIn();
          
          var imgage=$("#popup_image_content")
          imgage.attr("src", img.src);
          imgage.css("max-width","500px");
          imgage.css("max-height","500px");
      }
    
      
      function isBase64String(str) {
    // Base64 패턴 확인
    const base64Pattern = /^data:image\/[a-zA-Z]+;base64,/;
    return base64Pattern.test(str);
    }
      function enterSubmitUserId(event){
        if(event.keyCode===13){
          
          submitUserId();
        }
      }
      ws.onmessage = function (event) {
        const data = JSON.parse(event.data);
        var write_client=data["write_client"];
        var read_client_id=$("#client_name").text();
        var clietn_text=data["text"];
        var isEndodingText=isBase64String(clietn_text);

        var now = new Date();
        var hour = now.getHours();
        var num_minute = now.getMinutes();
        var str_minute=num_minute.toString();

        if (num_minute < 10) str_minute = "0" + str_minute;
        if (hour >= 12) {
            var half = "오후";
            hour -= 12;
        }
        else {
            var half = "오전";
        }
            if(hour==0){
              hour=12;
            }
        if(isEndodingText){
          console.log("이미지 전송됨");
          var to_div1 = '<div class="user_chat"> <div class="user_time">' + half + " " + hour + " : " + str_minute + '</div>  <div class="yellow"><img class="send_img" src="' + clietn_text + '"style="max-width: 150px; max-height: 150px;" onclick="click_img(this)"/></div> </div>';
          var to_div2= '<div class=friend_wrapper><div class="friend_name">'+write_client+'</div><div class="friend_chat"> <div class="white"><img class="send_img" src="' + clietn_text + '"style="max-width: 150px; max-height: 150px;" onclick="click_img(this)"/></div>  <div class="friend_time">' + half + " " + hour + " : " + str_minute + '</div> </div></div>';

        }
        else{
          var to_div1 = '<div class="user_chat"> <div class="user_time">' + half + " " + hour + " : " + str_minute + '</div>  <div class="yellow">' + clietn_text + '</div> </div>';
          var to_div2= '<div class=friend_wrapper><div class="friend_name">'+write_client+'</div><div class="friend_chat"> <div class="white">' + clietn_text + '</div>  <div class="friend_time">' + half + " " + hour + " : " + str_minute + '</div> </div></div>'; 
        }
         // let to_div2 = '<div class="friend_chat"> <div class="white">' + clietn_text + '</div>  <div class="friend_time">' + half + " " + hour + " : " + str_minute + '</div> </div>';
        if(write_client==read_client_id){
          $("#chat-content").append(to_div1)
        }
        else{
          $("#chat-content").append(to_div2)
        }
        $('#chat-content').scrollTop($('#chat-content')[0].scrollHeight);
      }
      function backBtn(){
        window.location.href = "/chatlist";
      }
      function sendMessage() {
        $("#textarea1").focus();
        var now = new Date();
        var hour = now.getHours();
        var num_minute = now.getMinutes();
        // num_minute=0;
        var str_minute=num_minute.toString();
        var text = $('#textarea1').val();
        if(text){
            text = text.replace(/(?:\r\n|\r|\n)/g, '<br/>');
            if (num_minute < 10) str_minute = "0" + str_minute;
            if (hour >= 12) {
                var half = "오후";
                hour -= 12;
            }
            else {
                var half = "오전";
            }
            if(hour==0){
              hour=12;
            }
            let to_div1 = '<div class="user_chat"> <div class="user_time">' + half + " " + hour + " : " + str_minute + '</div>  <div class="yellow">' + text + '</div> </div>';

            // $("#chat-content").append(to_div1);
            let c_id=$("#client_name").text();
            console.log(c_id);
            let f_id=$("#friend_name").text();
            console.log(f_id);
            let to_div2= '<div class=friend_wrapper><div class="friend_name">'+c_id+'</div><div class="friend_chat"> <div class="white">' + text + '</div>  <div class="friend_time">' + half + " " + hour + " : " + str_minute + '</div> </div></div>';
            ws.send(JSON.stringify({"write_client":c_id, "text":text}));
            // $("#chat-container2").append(to_div2);
            $('#textarea1').val('');
            $('#chat-content').scrollTop($('#chat-content')[0].scrollHeight);
            // $('#chat-container2').scrollTop($('#chat-container2')[0].scrollHeight);
            var data={"sender_name":c_id,"receiver_name":f_id, "in_sender_message":to_div1,"in_receiver_message":to_div2};
            $.ajax({
              url:"/postchat",
              type:"post",
              contentType:"application/json",
              dataType:"json",
              data:JSON.stringify(data),
              success:function(chat){
                console.log(chat);
              }           
            });
        }
        event.preventDefault();
      }
      function enterToSend(event) {
        if (event.keyCode === 13) {
          if (!event.shiftKey) {
                var text= $('#textarea1').val();
                if (!text) {
                    event.preventDefault();
                }
                else {
                    event.preventDefault();
                    sendMessage();
                    $('#textarea1').empty()
                }
            }
        }
      };
      function goGetClient(){
        window.location.href = "/getclientlistpage";
      }
      function getClientIdFromUrl() {
          // 현재 페이지의 URL을 가져옴
          var currentUrl = window.location.href;

          // URL을 '/'로 분할하여 배열로 만듦
          var urlParts = currentUrl.split('/');

          // 배열의 마지막 요소가 clientId일 것으로 가정하고 가져옴
          var chatroom_name = decodeURIComponent(urlParts[urlParts.length - 1]);
          var room_type= urlParts[urlParts.length - 2];
          return urlParts;
      }
    