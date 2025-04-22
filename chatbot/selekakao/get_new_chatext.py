from lxml import html

# Your HTML content
html_content = '''
<div id="kakaoWrap" style="height: 100%; padding-top: 0px; padding-bottom: 0px; min-width: auto;">
    <div class="chat_popup" style="padding-top: 70px;">
        <div class="popup_head"><strong class="screen_out">채팅방 레이어</strong>
            <div class="info_profile"><span class="wrap_thumb" style="width: 40px; height: 40px;"><img role="presentation"
                        src="https://img1.daumcdn.net/thumb/C100x100.mplusfriend/?fname=https%3A%2F%2Ft1.kakaocdn.net%2Frocket%2Fcenter-statics%2F202305080947_851d8300_a1a86cf4a%2Fresources%2Fimages%2Fchatbot%2Fthumb_default.png" draggable="false"
                        style="position: absolute; left: 0px; top: 0px; width: 40px; height: 40px;"></span>
                <div class="wrap_cont"><strong class="tit_user">휘둥그레</strong><span class="screen_out">상담상태</span><button class="btn_tooltip btn_state on" type="button"><span class="dot_state"></span> 상담중 <span class="ico_chat ico_arr_state"></span><span
                            class="layer_tooltip4"><span class="txt_tooltip">상담이 종료되면 클릭하여 &lt;상담 완료하기&gt;를 선택해 주세요.</span><span class="ico_chat ico_arr"></span></span></button></div>
            </div>
            <div class="area_util"><button type="button" class="btn_tooltip btn_util btn_mark"><span class="ico_chat ico_mark">중요 채팅방 활성화</span></button><button class="btn_tooltip btn_util btn_memo" type="button"><span class="ico_chat ico_memo">메모 내용 미리보기</span></button><button
                    class="btn_tooltip btn_util btn_menu" type="button"><span class="ico_chat ico_menu">사이드 메뉴 열기</span></button></div>
        </div>
        <div class="popup_body">
            <div class="" aria-disabled="false" style="position: relative; width: 100%; height: 100%; border: 0px;">
                <div id="room" class="fake_scroll" style="overflow: auto; height: 100%; padding-top: unset;">
                    <div style="overflow: auto;">
                        <div>
                            <div class="item_date"><em class="emph_date"><span>2023.05.15 월요일</span></em></div>
                            <div class="item_chat item_start item_me">
                                <div class="wrap_cont"><strong class="txt_user">클린베딩님이 보냄 <button type="button" class="btn_tooltip"><span class="ico_chat ico_guide">보낸 메시지 가이드</span><span class="layer_tooltip4"><span class="txt_tooltip">보낸 사람의 이름은 관리자만 확인할 수 있습니다.</span><span
                                                    class="ico_chat ico_arr"></span></span></button></strong>
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>알림톡/친구톡 메시지는 관리자센터에서 확인할 수 없습니다.</span></p><span class="ico_rocket ico_arr"></span>
                                            </div>
                                        </div>
                                        <div class=""><span class="txt_time"><span>오후</span><span class="num_txt"><span>03:09</span></span></span></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat item_start">
                                <div class="wrap_thumb" style="position: absolute; left: 15px;"><img alt="프로필 사진"
                                        src="https://img1.daumcdn.net/thumb/C100x100.mplusfriend/?fname=https%3A%2F%2Ft1.kakaocdn.net%2Frocket%2Fcenter-statics%2F202305080947_851d8300_a1a86cf4a%2Fresources%2Fimages%2Fchatbot%2Fthumb_default.png" role="presentation"
                                        draggable="false" style="width: 30px; height: 30px; vertical-align: middle;"></div>
                                <div class="wrap_cont"><strong class="txt_user">클린베딩 상담사</strong>
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>두었습니다.</span></p><span class="ico_rocket ico_arr"></span>
                                            </div>
                                        </div>
                                        <div class=""><span class="txt_time"><span>오후</span><span class="num_txt"><span>03:09</span></span></span></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat item_start item_me">
                                <div class="wrap_cont"><strong class="txt_user">정*식님이 보냄 <button type="button" class="btn_tooltip"><span class="ico_chat ico_guide">보낸 메시지 가이드</span><span class="layer_tooltip4"><span class="txt_tooltip">보낸 사람의 이름은 관리자만 확인할 수 있습니다.</span><span
                                                    class="ico_chat ico_arr"></span></span></button></strong>
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>요청이 접수되었습니다.
                                                    </span><br><span>■ 교체 안내메세지는 총 세차례 발송되며, 버튼은 한번만 눌러주셔도 접수가 완료됩니다.
                                                    </span><br><span>■ 배송완료 메시지 수신 전까지 침구를 그대로 두어주시기 바랍니다.
                                                    </span><br><span>■ 배송완료 메시지 수신 전까지 침구를 그대로 두어주시기 바랍니다.</span></p><span class="ico_rocket ico_arr"></span>
                                            </div>
                                        </div>
                                        <div class=""><span class="txt_time"><span>오후</span><span class="num_txt"><span>03:10</span></span></span></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat item_start">
                                <div class="wrap_thumb" style="position: absolute; left: 15px;"><img alt="프로필 사진"
                                        src="https://img1.daumcdn.net/thumb/C100x100.mplusfriend/?fname=https%3A%2F%2Ft1.kakaocdn.net%2Frocket%2Fcenter-statics%2F202305080947_851d8300_a1a86cf4a%2Fresources%2Fimages%2Fchatbot%2Fthumb_default.png" role="presentation"
                                        draggable="false" style="width: 30px; height: 30px; vertical-align: middle;"></div>
                                <div class="wrap_cont"><strong class="txt_user">클린베딩 상담사</strong>
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>아 근데 저번 이불 오지게 더럽던데오</span></p><span class="ico_rocket ico_arr"></span>
                                            </div>
                                        </div>
                                        <div class=""></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat">
                                <div class="wrap_cont">
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>두었습니다.</span></p>
                                            </div>
                                        </div>
                                        <div class=""></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat">
                                <div class="wrap_cont">
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>두었습니다.</span></p>
                                            </div>
                                        </div>
                                        <div class=""></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat">
                                <div class="wrap_cont">
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>두었습니다.</span></p>
                                            </div>
                                        </div>
                                        <div class=""></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat">
                                <div class="wrap_cont">
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>두었습니다.</span></p>
                                            </div>
                                        </div>
                                        <div class=""><span class="txt_time"><span>오후</span><span class="num_txt"><span>03:11</span></span></span></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat item_start item_me">
                                <div class="wrap_cont"><strong class="txt_user">정*식님이 보냄 <button type="button" class="btn_tooltip"><span class="ico_chat ico_guide">보낸 메시지 가이드</span><span class="layer_tooltip4"><span class="txt_tooltip">보낸 사람의 이름은 관리자만 확인할 수 있습니다.</span><span
                                                    class="ico_chat ico_arr"></span></span></button></strong>
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>요청이 접수되었습니다.
                                                    </span><br><span>■ 교체 안내메세지는 총 세차례 발송되며, 버튼은 한번만 눌러주셔도 접수가 완료됩니다.
                                                    </span><br><span>■ 배송완료 메시지 수신 전까지 침구를 그대로 두어주시기 바랍니다.
                                                    </span><br><span>■ 배송완료 메시지 수신 전까지 침구를 그대로 두어주시기 바랍니다.</span></p><span class="ico_rocket ico_arr"></span>
                                            </div>
                                        </div>
                                        <div class=""><span class="txt_time"><span>오후</span><span class="num_txt"><span>03:11</span></span></span></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat item_start item_me">
                                <div class="wrap_cont"><strong class="txt_user">정*식님이 보냄 <button type="button" class="btn_tooltip"><span class="ico_chat ico_guide">보낸 메시지 가이드</span><span class="layer_tooltip4"><span class="txt_tooltip">보낸 사람의 이름은 관리자만 확인할 수 있습니다.</span><span
                                                    class="ico_chat ico_arr"></span></span></button></strong>
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>요청이 접수되었습니다.
                                                    </span><br><span>
                                                    </span><br><span>■ 교체 안내메세지는 총 세차례 발송되며, 버튼은 한번만 눌러주셔도 접수가 완료됩니다.
                                                    </span><br><span>
                                                    </span><br><span>■ 배송완료 메시지 수신 전까지 침구를 그대로 두어주시기 바랍니다.</span></p><span class="ico_rocket ico_arr"></span>
                                            </div>
                                        </div>
                                        <div class=""></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat item_me">
                                <div class="wrap_cont">
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>요청이 접수되었습니다.
                                                    </span><br><span>
                                                    </span><br><span>■ 교체 안내메세지는 총 세차례 발송되며, 버튼은 한번만 눌러주셔도 접수가 완료됩니다.
                                                    </span><br><span>
                                                    </span><br><span>■ 배송완료 메시지 수신 전까지 침구를 그대로 두어주시기 바랍니다.</span></p>
                                            </div>
                                        </div>
                                        <div class=""><span class="txt_time"><span>오후</span><span class="num_txt"><span>03:17</span></span></span></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div>
                            <div class="item_date"><em class="emph_date"><span>2023.05.17 수요일</span></em></div>
                            <div class="item_chat item_start">
                                <div class="wrap_thumb" style="position: absolute; left: 15px;"><img alt="프로필 사진"
                                        src="https://img1.daumcdn.net/thumb/C100x100.mplusfriend/?fname=https%3A%2F%2Ft1.kakaocdn.net%2Frocket%2Fcenter-statics%2F202305080947_851d8300_a1a86cf4a%2Fresources%2Fimages%2Fchatbot%2Fthumb_default.png" role="presentation"
                                        draggable="false" style="width: 30px; height: 30px; vertical-align: middle;"></div>
                                <div class="wrap_cont"><strong class="txt_user">클린베딩 상담사</strong>
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>두었습니다.</span></p><span class="ico_rocket ico_arr"></span>
                                            </div>
                                        </div>
                                        <div class=""><span class="txt_time"><span>오후</span><span class="num_txt"><span>06:29</span></span></span></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat item_start item_me">
                                <div class="wrap_cont"><strong class="txt_user">박진우님이 보냄 <button type="button" class="btn_tooltip"><span class="ico_chat ico_guide">보낸 메시지 가이드</span><span class="layer_tooltip4"><span class="txt_tooltip">보낸 사람의 이름은 관리자만 확인할 수 있습니다.</span><span
                                                    class="ico_chat ico_arr"></span></span></button></strong>
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>요청이 접수되었습니다.
                                                    </span><br><span>
                                                    </span><br><span>■ 교체 안내 메시지는 총 세 차례 발송되며, 버튼은 한 번만 눌러주셔도 접수가 완료됩니다.
                                                    </span><br><span>■ 배송 완료 메시지 수신 전까지 침구를 그대로 두어주 시기 바랍니다.
                                                    </span><br><span>■ 배송일 오전 11시 이후에 배송을 접수해 주시면 답변이 발송되어도 배송이 취소될 수 있습니다.</span></p><span class="ico_rocket ico_arr"></span>
                                            </div>
                                        </div>
                                        <div class=""><span class="txt_time"><span>오후</span><span class="num_txt"><span>06:29</span></span></span></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat item_start">
                                <div class="wrap_thumb" style="position: absolute; left: 15px;"><img alt="프로필 사진"
                                        src="https://img1.daumcdn.net/thumb/C100x100.mplusfriend/?fname=https%3A%2F%2Ft1.kakaocdn.net%2Frocket%2Fcenter-statics%2F202305080947_851d8300_a1a86cf4a%2Fresources%2Fimages%2Fchatbot%2Fthumb_default.png" role="presentation"
                                        draggable="false" style="width: 30px; height: 30px; vertical-align: middle;"></div>
                                <div class="wrap_cont"><strong class="txt_user">클린베딩 상담사</strong>
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>두었다</span></p><span class="ico_rocket ico_arr"></span>
                                            </div>
                                        </div>
                                        <div class=""></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat">
                                <div class="wrap_cont">
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>두었습니다.</span></p>
                                            </div>
                                        </div>
                                        <div class=""></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat">
                                <div class="wrap_cont">
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>두었습니다.</span></p>
                                            </div>
                                        </div>
                                        <div class=""><span class="txt_time"><span>오후</span><span class="num_txt"><span>06:33</span></span></span></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat item_start item_me">
                                <div class="wrap_cont"><strong class="txt_user">박진우님이 보냄 <button type="button" class="btn_tooltip"><span class="ico_chat ico_guide">보낸 메시지 가이드</span><span class="layer_tooltip4"><span class="txt_tooltip">보낸 사람의 이름은 관리자만 확인할 수 있습니다.</span><span
                                                    class="ico_chat ico_arr"></span></span></button></strong>
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>요청이 접수되었습니다.
                                                    </span><br><span>
                                                    </span><br><span>■ 교체 안내 메시지는 총 세 차례 발송되며, 버튼은 한 번만 눌러주셔도 접수가 완료됩니다.
                                                    </span><br><span>■ 배송 완료 메시지 수신 전까지 침구를 그대로 두어주 시기 바랍니다.
                                                    </span><br><span>■ 배송일 오전 11시 이후에 배송을 접수해 주시면 답변이 발송되어도 배송이 취소될 수 있습니다.</span></p><span class="ico_rocket ico_arr"></span>
                                            </div>
                                        </div>
                                        <div class=""><span class="txt_time"><span>오후</span><span class="num_txt"><span>06:33</span></span></span></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat item_start">
                                <div class="wrap_thumb" style="position: absolute; left: 15px;"><img alt="프로필 사진"
                                        src="https://img1.daumcdn.net/thumb/C100x100.mplusfriend/?fname=https%3A%2F%2Ft1.kakaocdn.net%2Frocket%2Fcenter-statics%2F202305080947_851d8300_a1a86cf4a%2Fresources%2Fimages%2Fchatbot%2Fthumb_default.png" role="presentation"
                                        draggable="false" style="width: 30px; height: 30px; vertical-align: middle;"></div>
                                <div class="wrap_cont"><strong class="txt_user">클린베딩 상담사</strong>
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>안녕</span></p><span class="ico_rocket ico_arr"></span>
                                            </div>
                                        </div>
                                        <div class=""></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat">
                                <div class="wrap_cont">
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>두었습니다.</span></p>
                                            </div>
                                        </div>
                                        <div class=""><span class="txt_time"><span>오후</span><span class="num_txt"><span>06:38</span></span></span></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat item_start">
                                <div class="wrap_thumb" style="position: absolute; left: 15px;"><img alt="프로필 사진"
                                        src="https://img1.daumcdn.net/thumb/C100x100.mplusfriend/?fname=https%3A%2F%2Ft1.kakaocdn.net%2Frocket%2Fcenter-statics%2F202305080947_851d8300_a1a86cf4a%2Fresources%2Fimages%2Fchatbot%2Fthumb_default.png" role="presentation"
                                        draggable="false" style="width: 30px; height: 30px; vertical-align: middle;"></div>
                                <div class="wrap_cont"><strong class="txt_user">클린베딩 상담사</strong>
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>두었습니다.</span></p><span class="ico_rocket ico_arr"></span>
                                            </div>
                                        </div>
                                        <div class=""><span class="txt_time"><span>오후</span><span class="num_txt"><span>06:43</span></span></span></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat item_start item_me">
                                <div class="wrap_cont"><strong class="txt_user">박진우님이 보냄 <button type="button" class="btn_tooltip"><span class="ico_chat ico_guide">보낸 메시지 가이드</span><span class="layer_tooltip4"><span class="txt_tooltip">보낸 사람의 이름은 관리자만 확인할 수 있습니다.</span><span
                                                    class="ico_chat ico_arr"></span></span></button></strong>
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>요청이 접수되었습니다.
                                                    </span><br><span>
                                                    </span><br><span>■ 교체 안내 메시지는 총 세 차례 발송되며, 버튼은 한 번만 눌러주셔도 접수가 완료됩니다.
                                                    </span><br><span>■ 배송 완료 메시지 수신 전까지 침구를 그대로 두어주 시기 바랍니다.
                                                    </span><br><span>■ 배송일 오전 11시 이후에 배송을 접수해 주시면 답변이 발송되어도 배송이 취소될 수 있습니다.</span></p><span class="ico_rocket ico_arr"></span>
                                            </div>
                                        </div>
                                        <div class=""><span class="txt_time"><span>오후</span><span class="num_txt"><span>06:43</span></span></span></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat item_start">
                                <div class="wrap_thumb" style="position: absolute; left: 15px;"><img alt="프로필 사진"
                                        src="https://img1.daumcdn.net/thumb/C100x100.mplusfriend/?fname=https%3A%2F%2Ft1.kakaocdn.net%2Frocket%2Fcenter-statics%2F202305080947_851d8300_a1a86cf4a%2Fresources%2Fimages%2Fchatbot%2Fthumb_default.png" role="presentation"
                                        draggable="false" style="width: 30px; height: 30px; vertical-align: middle;"></div>
                                <div class="wrap_cont"><strong class="txt_user">클린베딩 상담사</strong>
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>안녕하세요 </span></p><span class="ico_rocket ico_arr"></span>
                                            </div>
                                        </div>
                                        <div class=""><span class="txt_time"><span>오후</span><span class="num_txt"><span>11:42</span></span></span></div>
                                    </div>
                                </div>
                            </div>
                            <p class="txt_check" style="margin-bottom: 10px; width: 141px;"><span class="ico_rocket"></span> 여기까지 읽었습니다.</p>
                            <div class="item_chat item_start">
                                <div class="wrap_thumb" style="position: absolute; left: 15px;"><img alt="프로필 사진"
                                        src="https://img1.daumcdn.net/thumb/C100x100.mplusfriend/?fname=https%3A%2F%2Ft1.kakaocdn.net%2Frocket%2Fcenter-statics%2F202305080947_851d8300_a1a86cf4a%2Fresources%2Fimages%2Fchatbot%2Fthumb_default.png" role="presentation"
                                        draggable="false" style="width: 30px; height: 30px; vertical-align: middle;"></div>
                                <div class="wrap_cont"><strong class="txt_user">클린베딩 상담사</strong>
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>1</span></p><span class="ico_rocket ico_arr"></span>
                                            </div>
                                        </div>
                                        <div class=""></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat">
                                <div class="wrap_cont">
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>2</span></p>
                                            </div>
                                        </div>
                                        <div class=""></div>
                                    </div>
                                </div>
                            </div>
                            <div class="item_chat">
                                <div class="wrap_cont">
                                    <div class="set_chat">
                                        <div class="bubble_chat">
                                            <div class="box_bubble">
                                                <p class="txt_chat"><span>3</span></p>
                                            </div>
                                        </div>
                                        <div class=""><span class="txt_time"><span>오후</span><span class="num_txt"><span>11:43</span></span></span></div>
                                    </div>
                                </div>
                            </div>
                        </div><svg class="svg_source" aria-hidden="true" focusable="false">
                            <defs>
                                <path id="shapeSquircle" d="M15,30 C3.95839286,30 0,26.041875 0,15 C0,4.37491071 3.95839286,0 15,0 C26.041875,0 30,3.95839286 30,15 C30,26.041875 26.041875,30 15,30 Z"></path>
                            </defs>
                            <clipPath id="clipThumb">
                                <use xlink:href="#shapeSquircle"></use>
                            </clipPath>
                            <symbol id="icoBubble" viewBox="0 0 12 14">
                                <g>
                                    <path
                                        d="M0.966552734,3.28161621 C1.12122295,3.17869178 1.22477011,3.11011512 1.2771942,3.07588623 C3.37094947,1.70882569 7.2785514,0.683530274 13,0 C9,2.02897135 6.96226357,6.37863375 6.88679071,13.0489872 C6.8824443,13.4331262 6.8824443,13.7501305 6.88679071,14 L0.966552734,3.28161621 Z"
                                        transform="translate(6.500000, 7.000000) scale(-1, 1) translate(-6.500000, -7.000000)"></path>
                                </g>
                            </symbol>
                            <symbol id="icoBubble2" viewBox="0 0 28 13">
                                <g>
                                    <path
                                        d="M14.864778,0.522692003 C17.541669,5.44839659 19.946968,8.64655407 22.080673,10.1171645 C24.441687,11.7444431 26.414796,12.6686198 28,12.8896944 L0,12.8896944 C1.681201,12.7008463 3.656135,11.7766697 5.9248,10.1171645 C7.975344,8.61721287 10.371514,5.41554113 13.113312,0.512149253 L13.113297,0.512140953 C13.382843,0.0300891825 13.992133,-0.142181002 14.474185,0.127364723 C14.639119,0.219589713 14.774546,0.356659013 14.864778,0.522692003 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoArr1" viewBox="0 0 16 9">
                                <g>
                                    <path d="M13.9698485,0.348780669 L15.1012193,1.48015152 L8.03015152,8.55121933 L7.99978067,8.52078067 L7.96984848,8.55121933 L0.898780669,1.48015152 L2.03015152,0.348780669 L7.99978067,6.31878067 L13.9698485,0.348780669 Z"></path>
                                </g>
                            </symbol>
                            <symbol id="icoArr2" viewBox="0 0 6 10">
                                <g>
                                    <polyline points="1 1 5 5 1 9" stroke-width="1.2" fill="none"></polyline>
                                </g>
                            </symbol>
                            <symbol id="icoArr3" viewBox="0 0 9 10">
                                <g>
                                    <rect x="4" y="0" width="1" height="9" stroke-width="0"></rect>
                                    <polyline points="7 3 7 8 2 8" fill="none" transform="translate(4.500000, 5.500000) rotate(-315.000000) translate(-4.500000, -5.500000)"></polyline>
                                </g>
                            </symbol>
                            <symbol id="icoArr4" viewBox="0 0 84 15">
                                <g>
                                    <polyline points="0 14 84 14 70.8 1" fill="none"></polyline>
                                </g>
                            </symbol>
                            <symbol id="icoArr5" viewBox="0 0 20 20">
                                <g>
                                    <path d="M12,4.13603897 L18.363961,10.5 L12,16.863961 L11.2928932,16.1568542 L16.449,10.999039 L2,11 L2,10 L16.449,9.99903897 L11.2928932,4.84314575 L12,4.13603897 Z"></path>
                                </g>
                            </symbol>
                            <symbol id="icoRefresh" viewBox="0 0 11 13">
                                <g>
                                    <path
                                        d="M5.5,0.35 C6.88766811,0.35 8.18946332,0.902261207 9.14924079,1.86605692 C10.1037673,2.82457968 10.65,4.11989336 10.65,5.5 C10.65,6.89947176 10.0882613,8.21136754 9.1099439,9.1729846 C8.31421811,9.95512696 7.29095345,10.4581742 6.18158561,10.6051526 L7.04565684,11.5407703 L6.16718993,12.4282573 L4.144,10.235 L3.45749777,9.5407703 L3.48,9.515 L3.45749777,9.49011521 L4.144,8.795 L6.16718993,6.60262826 L7.04565684,7.49011521 L5.177,9.515 L5.5,9.865 L5.5,9.35 C6.44516219,9.35 7.33500976,9.00863288 8.0292489,8.4027922 L8.19865233,8.24586667 C8.93079632,7.52622073 9.35,6.54720405 9.35,5.5 C9.35,4.46726239 8.94238811,3.5006684 8.22808374,2.78337349 C7.50983574,2.06211844 6.53838635,1.65 5.5,1.65 C4.40273712,1.65 3.38104404,2.11059468 2.65556396,2.90540762 C2.01227276,3.61017704 1.65,4.52596657 1.65,5.5 C1.65,6.01209214 1.74967671,6.50917447 1.94089919,6.97118247 L1.94089919,6.97118247 L0.739720258,7.46834359 C0.483537575,6.84938681 0.35,6.18344218 0.35,5.5 C0.35,4.1984703 0.835564562,2.97101134 1.69540128,2.02900154 C2.66467962,0.967090962 4.03351341,0.35 5.5,0.35 Z"
                                        transform="translate(5.500000, 6.500000) scale(-1, -1) translate(-5.500000, -6.500000)"></path>
                                </g>
                            </symbol>
                            <symbol id="icoRefresh2" viewBox="0 0 18 18">
                                <g fill="none" transform="translate(3.000000, 1.000000)">
                                    <path d="M2.6455,12.261 C1.3475,11.336 0.4995,9.818 0.4995,8.102 C0.4995,5.284 2.7845,3 5.6025,3 L6,3" stroke-width="1.2" stroke-linejoin="round"></path>
                                    <path d="M9.653,3.74 C10.954,4.664 11.802,6.184 11.802,7.901 C11.802,10.719 9.518,13.003 6.7,13.003 L6.41584778,13.003" stroke-width="1.2" stroke-linejoin="round"></path>
                                    <polyline stroke-width="1.1" points="4.791 0.5 7.291 3.00048819 4.791 5.5"></polyline>
                                    <polyline stroke-width="1.1" points="7.5445 10.5 5.0445 13 7.5445 15.5"></polyline>
                                </g>
                            </symbol>
                            <symbol id="icoClose" viewBox="0 0 10 9">
                                <g>
                                    <path
                                        d="M8.36092351,0.0370998077 L9.23120878,0.932768397 L5.74935609,4.51509981 L9.23120878,8.09811711 L8.36092351,8.9937857 L4.87935609,5.41009981 L1.39864136,8.9937857 L0.528356088,8.09811711 L4.00935609,4.51509981 L0.528356088,0.932768397 L1.39864136,0.0370998077 L4.87935609,3.62009981 L8.36092351,0.0370998077 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoClose2" viewBox="0 0 10 9">
                                <g>
                                    <path
                                        d="M8.36092351,0.0370998077 L9.23120878,0.932768397 L5.74935609,4.51509981 L9.23120878,8.09811711 L8.36092351,8.9937857 L4.87935609,5.41009981 L1.39864136,8.9937857 L0.528356088,8.09811711 L4.00935609,4.51509981 L0.528356088,0.932768397 L1.39864136,0.0370998077 L4.87935609,3.62009981 L8.36092351,0.0370998077 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoClose3" viewBox="0 0 10 9">
                                <g>
                                    <path
                                        d="M8.36092351,0.0370998077 L9.23120878,0.932768397 L5.74935609,4.51509981 L9.23120878,8.09811711 L8.36092351,8.9937857 L4.87935609,5.41009981 L1.39864136,8.9937857 L0.528356088,8.09811711 L4.00935609,4.51509981 L0.528356088,0.932768397 L1.39864136,0.0370998077 L4.87935609,3.62009981 L8.36092351,0.0370998077 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoDownload" viewBox="0 0 14 15">
                                <g>
                                    <path
                                        d="M12.6,13.2 C12.9313708,13.2 13.2,13.4686292 13.2,13.8 C13.2,14.1313708 12.9313708,14.4 12.6,14.4 L0.8,14.4 C0.46862915,14.4 0.2,14.1313708 0.2,13.8 C0.2,13.4686292 0.46862915,13.2 0.8,13.2 L12.6,13.2 Z M6.65,0.7 C7.06421356,0.7 7.4,1.03578644 7.4,1.45 L7.4,8.95 L7.395,9.002 L11.188796,5.81997492 L12.0115642,6.80051181 L6.781,11.189 L6.68879602,11.3000251 L6.669,11.284 L6.64925305,11.3000251 L6.556,11.189 L1.32648491,6.80051181 L2.14925305,5.81997492 L5.90019748,8.96738278 C5.90006606,8.96160442 5.9,8.95580993 5.9,8.95 L5.9,1.45 C5.9,1.03578644 6.23578644,0.7 6.65,0.7 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoUpload" viewBox="0 0 14 18">
                                <g>
                                    <path
                                        d="M12.6,16.2 C12.9313708,16.2 13.2,16.4686292 13.2,16.8 C13.2,17.1313708 12.9313708,17.4 12.6,17.4 L0.8,17.4 C0.46862915,17.4 0.2,17.1313708 0.2,16.8 C0.2,16.4686292 0.46862915,16.2 0.8,16.2 L12.6,16.2 Z M6.75,3 C7.16421356,3 7.5,3.33578644 7.5,3.75 L7.5,12.25 C7.5,12.6642136 7.16421356,13 6.75,13 C6.33578644,13 6,12.6642136 6,12.25 L6,3.75 C6,3.33578644 6.33578644,3 6.75,3 Z M6.68879602,0.819974923 L6.781,0.930974922 L12.0115642,5.31948819 L11.188796,6.30002508 L6.669,2.50697492 L2.14925305,6.30002508 L1.32648491,5.31948819 L6.556,0.930974922 L6.64925305,0.819974922 L6.669,0.835974922 L6.68879602,0.819974923 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoPlay" viewBox="0 0 14 16">
                                <g>
                                    <polygon transform="translate(7.000000, 8.000000) rotate(90.000000) translate(-7.000000, -8.000000) " points="7 1 15 15 -1 15"></polygon>
                                </g>
                            </symbol>
                            <symbol id="icoPause" viewBox="0 0 12 16">
                                <g>
                                    <path d="M4,0 L4,16 L0,16 L0,0 L4,0 Z M12,0 L12,16 L8,16 L8,0 L12,0 Z"></path>
                                </g>
                            </symbol>
                            <symbol id="icoImage" viewBox="0 0 24 16">
                                <g>
                                    <polyline stroke="#FFFFFF" stroke-width="2" points="1.13686838e-13 15 7.25558794 7.74441206 14.2591964 14.7480205 18.3236109 10.6836059 23.263467 15.623462"></polyline>
                                    <circle fill="#FFFFFF" cx="17.2641284" cy="2" r="2"></circle>
                                </g>
                            </symbol>
                            <symbol id="icoVideo" viewBox="0 0 20 12">
                                <g>
                                    <path
                                        d="M11,0 C12.1045695,-2.02906125e-16 13,0.8954305 13,2 L13,10 C13,11.1045695 12.1045695,12 11,12 L2,12 C0.8954305,12 1.3527075e-16,11.1045695 0,10 L0,2 C-1.3527075e-16,0.8954305 0.8954305,2.02906125e-16 2,0 L11,0 Z M20,1 L20,11 L14,6 L20,1 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoNoimage" viewBox="0 0 60 60">
                                <g>
                                    <path
                                        d="M50.690895,4.75251845 L52.0488158,6.14170697 L46,12.313 L46,32.5172001 C46,33.3361279 45.3319976,34 44.5086495,34 L24.749,34 L18.4679436,40.411818 L17.1100228,39.0226295 L50.690895,4.75251845 Z M44.5086495,4.54747351e-13 C45.3322996,4.54747351e-13 46,0.663917791 46,1.48279994 L46,6.571 L43.999,8.616 L44,2 L43.4118373,1.9990891 C38.3298996,1.9956624 2.03034481,2 2.03034481,2 L2.03009536,2.03552 C2.02558451,3.188 2,32 2,32 C2,32.0023571 11.2778,32.0024985 21.112268,32.0019863 L19.155,34 L1.49135054,34 C0.667700379,34 5.68434189e-13,33.3360822 5.68434189e-13,32.5172001 L5.68434189e-13,1.48279994 C5.68434189e-13,0.663872148 0.668002371,4.54747351e-13 1.49135054,4.54747351e-13 L44.5086495,4.54747351e-13 Z M43.999,14.355 L36.351,22.16 L37.8852172,23.6557759 L36.5263228,25.0146703 L35.006,23.533 L26.708,32.001 L34.2032515,32.0010153 C39.8714901,32.000493 44,32 44,32 L43.999,14.355 Z M17.7671693,14.0069166 L17.8773608,14.1159282 L17.9758215,14.0185434 L26.0550507,22.0970425 L31.1185731,17.0337314 L32.4773583,18.3925167 L26.1133973,24.7564777 L26.0034319,24.6461624 L25.915113,24.734483 L17.8363486,16.6544416 L9.5955648,24.8960916 L8.23677955,23.5373064 L17.7671693,14.0069166 Z M29.8309067,9.01601816 C31.0690636,9.01601816 32.072788,10.0415627 32.072788,11.306636 C32.072788,12.5717093 31.0690636,13.5972538 29.8309067,13.5972538 C28.5927499,13.5972538 27.5890255,12.5717093 27.5890255,11.306636 C27.5890255,10.0415627 28.5927499,9.01601816 29.8309067,9.01601816 Z"
                                        transform="translate(7.000000, 13.000000)"></path>
                                </g>
                            </symbol>
                            <symbol id="icoNovideo" viewBox="0 0 60 60">
                                <g>
                                    <path
                                        d="M50.690895,4.75251845 L52.0488158,6.14170697 L46,12.313 L46,32.5172001 C46,33.3361279 45.3319976,34 44.5086495,34 L24.749,34 L18.4679436,40.411818 L17.1100228,39.0226295 L50.690895,4.75251845 Z M44.5086495,4.54747351e-13 C45.3322996,4.54747351e-13 46,0.663917791 46,1.48279994 L46,6.571 L43.999,8.616 L44,2 L43.4118373,1.9990891 C38.3298996,1.9956624 2.03034481,2 2.03034481,2 L2.03009536,2.03552 C2.02558451,3.188 2,32 2,32 C2,32.0023571 11.2778,32.0024985 21.112268,32.0019863 L19.155,34 L1.49135054,34 C0.667700379,34 3.41060513e-13,33.3360822 3.41060513e-13,32.5172001 L3.41060513e-13,1.48279994 C3.41060513e-13,0.663872148 0.668002371,4.54747351e-13 1.49135054,4.54747351e-13 L44.5086495,4.54747351e-13 Z M43.999,14.355 L26.708,32.001 L34.2032515,32.0010153 C39.8714901,32.000493 44,32 44,32 L43.999,14.355 Z M20,11 L30,17 L20,23 L20,11 Z"
                                        transform="translate(7.000000, 13.000000)"></path>
                                </g>
                            </symbol>
                            <symbol id="icoImg" viewBox="0 0 20 20">
                                <g>
                                    <path
                                        d="M18.9,0 C19.5075132,0 20,0.492486775 20,1.1 L20,18.9 C20,19.5075132 19.5075132,20 18.9,20 L1.1,20 C0.492486775,20 0,19.5075132 0,18.9 L0,1.1 C0,0.492486775 0.492486775,0 1.1,0 L18.9,0 Z M18.6,1.4 L1.4,1.4 L1.4,18.6 L18.6,18.6 L18.6,1.4 Z M7.9393098,9.23814669 L12.3793829,13.6782198 L16.5172221,9.54038059 L17.4364609,10.4596194 L12.3793829,15.5166974 L7.9393098,11.0766243 L3.38477287,15.6311613 L2.46553405,14.7119224 L7.9393098,9.23814669 Z M13.9935065,5.23809524 C14.6211028,5.23809524 15.1298701,5.74686257 15.1298701,6.37445887 C15.1298701,7.00205518 14.6211028,7.51082251 13.9935065,7.51082251 C13.3659102,7.51082251 12.8571429,7.00205518 12.8571429,6.37445887 C12.8571429,5.74686257 13.3659102,5.23809524 13.9935065,5.23809524 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoPdf" viewBox="0 0 23 21">
                                <g>
                                    <path
                                        d="M12.3989942,-0.0154957397 C12.5774843,0.11183964 12.8145112,0.335496189 13.0465182,0.661226605 C13.7806443,1.69191613 13.9269856,3.02472381 13.1339069,4.57897463 L11.4783208,7.48523453 L11.34,7.715 L14.66,13.371 L17.5685576,13.3719203 C18.2026046,13.3719203 18.7781237,13.4572609 19.2858443,13.6005921 C19.6009041,13.6895345 19.8305712,13.7823247 19.9620649,13.8500761 C20.9881912,14.3679303 21.65,15.4180826 21.65,16.5853303 C21.65,18.2784883 20.2707436,19.65 18.5716951,19.65 C17.4548901,19.65 16.644382,19.1983363 15.9360747,18.1128039 L13.916,14.671 L7.16,14.671 L5.12112565,18.0649619 C4.37539189,19.2491564 3.60216691,19.65 2.39604492,19.65 C0.700028537,19.65 -0.65,18.2822199 -0.65,16.5853303 C-0.65,15.4182067 0.0122620424,14.3680011 1.03375503,13.85251 C1.17002237,13.7823247 1.39968945,13.6895345 1.7147493,13.6005921 C2.22246989,13.4572609 2.79798895,13.3719203 3.43203595,13.3719203 L6.424,13.371 L9.827,7.707 L9.69769312,7.48542456 L7.95235333,4.582795 L7.94432876,4.56868464 L7.92881956,4.540501 C7.90794806,4.50148355 7.90794806,4.50148355 7.87983768,4.44594617 C7.83141038,4.34873295 7.78191234,4.23901468 7.73362211,4.11807409 C7.59591161,3.77318467 7.49263832,3.40140281 7.44401002,3.01188429 C7.29954738,1.85472122 7.66405467,0.786103376 8.67829451,0.0101177168 L8.68468683,0.00495019319 L8.69583131,-0.00387328778 L8.72947884,-0.0295469277 C8.7755194,-0.063345055 8.79925521,-0.0801104766 8.84073192,-0.107715638 C8.95487744,-0.183686128 9.08435674,-0.258615499 9.22825839,-0.328257768 C10.2263627,-0.811297774 11.3518042,-0.811297774 12.3989942,-0.0154957397 Z M5.64343609,14.6719203 L3.43203595,14.6719203 C2.92189785,14.6719203 2.46448953,14.7397469 2.06793959,14.8516942 C1.84043711,14.9159189 1.69099688,14.9762959 1.62423735,15.0106559 C1.03120191,15.3099425 0.65,15.914447 0.65,16.5853303 C0.65,17.5680236 1.42182756,18.35 2.39604492,18.35 C3.16769566,18.35 3.52050933,18.1670997 4.01394479,17.383812 L5.64343609,14.6719203 Z M17.5685576,14.6719203 L15.4234319,14.6719203 L17.0407928,17.4282389 C17.4958552,18.1247798 17.9000117,18.35 18.5716951,18.35 C19.554407,18.35 20.35,17.5588743 20.35,16.5853303 C20.35,15.9141741 19.9691277,15.3098093 19.3715826,15.008222 C19.3095967,14.9762959 19.1601565,14.9159189 18.932654,14.8516942 C18.536104,14.7397469 18.0786957,14.6719203 17.5685576,14.6719203 Z M10.5775453,8.98435623 L7.94119457,13.3719203 L13.1531082,13.3719203 L10.5775453,8.98435623 Z M9.79456956,0.841909594 C9.70629925,0.884628663 9.6277474,0.930086438 9.56101145,0.974503095 C9.53917964,0.989033435 9.52598694,0.998351896 9.50646233,1.01270863 L9.497,1.019 L9.48443033,1.02979021 C8.85060589,1.51497357 8.6431516,2.12316265 8.73399632,2.85083972 C8.76772559,3.12101525 8.84183581,3.38781059 8.94093765,3.63600647 C8.97553174,3.72264573 9.01042632,3.79999369 9.04345029,3.8662862 C9.06125052,3.90143869 9.06125052,3.90143869 9.07222419,3.92193341 L10.5818141,6.43312584 L11.9900034,3.96206463 C12.5401614,2.88281651 12.4503725,2.0650613 11.9876546,1.41542011 C11.8479708,1.21930856 11.713307,1.0922409 11.6283288,1.03125924 C11.0006392,0.55447186 10.3885014,0.55447186 9.79456956,0.841909594 Z"
                                        transform="translate(1.000000, 1.000000)"></path>
                                </g>
                            </symbol>
                            <symbol id="icoXlsx" viewBox="0 0 21 19">
                                <g>
                                    <path
                                        d="M5.2,0.8 L5.2,2.2 L4.078,2.199 L9.75,8.457 L15.42,2.199 L14.3,2.2 L14.3,0.8 L19.2,0.8 L19.2,2.2 L17.31,2.199 L17.1603091,2.3649364 L17.25,2.4 L13.0793091,6.8679364 L10.694,9.5 L11.4993091,10.3889364 L11.4993091,12.4729364 L9.75,10.542 L4.079,16.799 L5.2,16.8 L5.2,18.2 L0.3,18.2 L0.3,16.8 L2.189,16.799 L8.805,9.5 L6.41930913,6.8679364 L2.25,2.4 L2.33830913,2.3639364 L2.189,2.199 L0.3,2.2 L0.3,0.8 L5.2,0.8 Z M21,17 L21,18 L13,18 L13,17 L21,17 Z M21,14 L21,15 L13,15 L13,14 L21,14 Z M21,11 L21,12 L13,12 L13,11 L21,11 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoMov" viewBox="0 0 20 20">
                                <g>
                                    <path
                                        d="M19,0 C19.5522847,0 20,0.44771525 20,1 L20,19 C20,19.5522847 19.5522847,20 19,20 L1,20 C0.44771525,20 0,19.5522847 0,19 L0,1 C0,0.44771525 0.44771525,0 1,0 L19,0 Z M18.6,1.4 L1.4,1.4 L1.4,18.6 L18.6,18.6 L18.6,1.4 Z M7.49460944,6.1119812 C7.58162291,6.1119812 7.66713007,6.13468886 7.74267891,6.17785963 L13.6851006,9.57352919 C13.9248594,9.71053418 14.0081577,10.0159615 13.8711528,10.2557202 C13.8268581,10.3332359 13.7626163,10.3974777 13.6851006,10.4417723 L7.74267891,13.8374419 C7.50292019,13.9744469 7.19749286,13.8911485 7.06048787,13.6513898 C7.0173171,13.5758409 6.99460944,13.4903338 6.99460944,13.4033203 L6.99460944,6.6119812 C6.99460944,6.33583883 7.21846707,6.1119812 7.49460944,6.1119812 Z M8.19471142,7.81706092 L8.19471142,12.1970609 L12.0267114,10.0070609 L8.19471142,7.81706092 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoAudio" viewBox="0 0 22 20">
                                <g transform="translate(0.000000, 0.217391)">
                                    <path
                                        d="M12.8999701,0.243711318 C12.9649,0.330266575 13,0.435549041 13,0.543751206 L13,18.613296 C13,18.8894383 12.7761424,19.113296 12.5,19.113296 C12.4018852,19.113296 12.3059387,19.0844294 12.2241117,19.030292 L4.5,13.9199511 L0.5,13.9199511 C0.223857625,13.9199511 0,13.6960935 0,13.4199511 L0,6.41995109 C0,6.14380871 0.223857625,5.91995109 0.5,5.91995109 L4.5,5.91995109 L12.1999601,0.143781125 C12.4208575,-0.0219263297 12.7342626,0.0228139418 12.8999701,0.243711318 Z M11.6,2.34397561 L5.34011169,7.03986731 C5.09775696,7.22167112 4.80296606,7.31995109 4.5,7.31995109 L1.4,7.31995109 L1.4,12.5199511 L4.5,12.5199511 C4.77472142,12.5199511 5.04337166,12.6007774 5.27248712,12.7523623 L11.6,16.938701 L11.6,2.34397561 Z M14.816634,3.22660274 C18.2066469,3.38156719 20.9075,6.17904305 20.9075,9.60733696 C20.9075,13.0356309 18.2066469,15.8331067 14.816634,15.9880712 L14.8170065,14.5861398 C17.4332603,14.4324873 19.5075,12.2621445 19.5075,9.60733696 C19.5075,6.95252944 17.4332603,4.78218658 14.8170065,4.62853416 L14.816634,3.22660274 Z M14.8177359,6.73500037 C16.2725729,6.88402472 17.4075,8.11314263 17.4075,9.60733696 C17.4075,11.1015313 16.2725729,12.3306492 14.8177359,12.4796735 L14.8169767,11.0651877 C15.4962039,10.9275671 16.0075,10.3271618 16.0075,9.60733696 C16.0075,8.88751209 15.4962039,8.28710684 14.8169767,8.14948621 L14.8177359,6.73500037 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoPpt" viewBox="0 0 20 20">
                                <g>
                                    <path
                                        d="M10,0 L10,10 L20,10 C20,15.5228475 15.5228475,20 10,20 C4.4771525,20 0,15.5228475 0,10 C0,4.4771525 4.4771525,0 10,0 Z M8.6,1.51338233 C4.5162226,2.18197689 1.4,5.72707205 1.4,10 C1.4,14.7496488 5.25035115,18.6 10,18.6 C14.1839086,18.6 17.6699949,15.6122675 18.4411045,11.6539568 L18.4866177,11.4 L8.6,11.4 L8.6,1.51338233 Z M19,6.6 L19,7.8 L12,7.8 L12,6.6 L19,6.6 Z M19,3.8 L19,5 L12,5 L12,3.8 L19,3.8 Z M19,1 L19,2.2 L12,2.2 L12,1 L19,1 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoDoc" viewBox="0 0 18 21">
                                <g>
                                    <path
                                        d="M12.6322343,0 L18,5.27600861 L18,20.6 C18,20.8209139 17.8209139,21 17.6,21 L0.4,21 C0.1790861,21 0,20.8209139 0,20.6 L0,0.4 C0,0.1790861 0.1790861,0 0.4,0 L12.6322343,0 Z M11.3,1.399 L1.4,1.4 L1.4,19.6 L16.6,19.6 L16.6,6.7 L11.3,6.7 L11.3,1.399 Z M14,12 L14,13.2 L4,13.2 L4,12 L14,12 Z M14,9 L14,10.2 L4,10.2 L4,9 L14,9 Z M8,6 L8,7.2 L4,7.2 L4,6 L8,6 Z M12.7,2.029 L12.7,5.3 L16.028,5.3 L12.7,2.029 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoZip" viewBox="0 0 20 20">
                                <g>
                                    <path
                                        d="M19,0 C19.5522847,0 20,0.44771525 20,1 L20,19 C20,19.5522847 19.5522847,20 19,20 L1,20 C0.44771525,20 0,19.5522847 0,19 L0,1 C0,0.44771525 0.44771525,0 1,0 L19,0 Z M9.5,1.399 L1.4,1.4 L1.4,18.6 L18.6,18.6 L18.6,1.4 L10.5,1.399 L10.5,3 L12.0952381,3 L12.0952381,4 L10.5,4 L10.5,5 L12.0952381,5 L12.0952381,6 L10.5,6 L10.5,7 L9.5,7 L9.5,6 L8.0952381,6 L8.0952381,5 L9.5,5 L9.5,4 L8.0952381,4 L8.0952381,3 L9.5,3 L9.5,1.399 Z M11.9285714,7.11904762 L11.9285714,10.4761905 C11.9285714,11.5413111 11.0651206,12.4047619 10,12.4047619 C8.93487941,12.4047619 8.07142857,11.5413111 8.07142857,10.4761905 L8.07142857,7.11904762 L11.9285714,7.11904762 Z M10.9285714,8.11904762 L9.07142857,8.11904762 L9.07142857,10.4761905 C9.07142857,10.9890263 9.48716416,11.4047619 10,11.4047619 C10.5128358,11.4047619 10.9285714,10.9890263 10.9285714,10.4761905 L10.9285714,8.11904762 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoEtc" viewBox="0 0 20 20">
                                <g fill="none">
                                    <path
                                        d="M5.86133669,0.7 L1,0.7 C0.834314575,0.7 0.7,0.834314575 0.7,1 L0.7,19 C0.7,19.1656854 0.834314575,19.3 1,19.3 L19,19.3 C19.1656854,19.3 19.3,19.1656854 19.3,19 L19.3,3.85714286 C19.3,3.69145743 19.1656854,3.55714286 19,3.55714286 L8.24066146,3.55714286 L5.86133669,0.7 Z">
                                    </path>
                                    <path
                                        d="M5.86133669,0.7 L1,0.7 C0.834314575,0.7 0.7,0.834314575 0.7,1 L0.7,19 C0.7,19.1656854 0.834314575,19.3 1,19.3 L19,19.3 C19.1656854,19.3 19.3,19.1656854 19.3,19 L19.3,3.85714286 C19.3,3.69145743 19.1656854,3.55714286 19,3.55714286 L8.24066146,3.55714286 L5.86133669,0.7 Z M8.42809346,3.15714286 L19.7,3.15714286 L19.7,19.7 L0.3,19.7 L0.3,0.3 L6.04876868,0.3 L8.42809346,3.15714286 Z M5.95238095,10.7 C5.78669553,10.7 5.65238095,10.8343146 5.65238095,11 C5.65238095,11.1656854 5.78669553,11.3 5.95238095,11.3 C6.11806638,11.3 6.25238095,11.1656854 6.25238095,11 C6.25238095,10.8343146 6.11806638,10.7 5.95238095,10.7 Z M9.95238095,10.7 C9.78669553,10.7 9.65238095,10.8343146 9.65238095,11 C9.65238095,11.1656854 9.78669553,11.3 9.95238095,11.3 C10.1180664,11.3 10.252381,11.1656854 10.252381,11 C10.252381,10.8343146 10.1180664,10.7 9.95238095,10.7 Z M13.952381,10.7 C13.7866955,10.7 13.652381,10.8343146 13.652381,11 C13.652381,11.1656854 13.7866955,11.3 13.952381,11.3 C14.1180664,11.3 14.252381,11.1656854 14.252381,11 C14.252381,10.8343146 14.1180664,10.7 13.952381,10.7 Z M19.3,0.7 L19.3,1 L19.6,0.7 L20,0.7 L19.8,0.5 L20,0.3 L19.6,0.3 L19.3,0 L19.3,0.3 L10.7,0.3 L10.7,0 L10.4,0.3 L10,0.3 L10.2,0.5 L10,0.7 L10.4,0.7 L10.7,1 L10.7,0.7 L19.3,0.7 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoEtcUnit" viewBox="0 0 20 20">
                                <g>
                                    <path d="M12.632 0 18 5.276V20.6a.4.4 0 0 1-.4.4H.4a.4.4 0 0 1-.4-.4V.4C0 .18.18 0 .4 0h12.232zM11.3 1.399 1.4 1.4v18.2h15.2V6.7h-5.3V1.399zM16.028 5.3 12.7 2.029V5.3h3.328z"></path>
                                </g>
                            </symbol>
                            <symbol id="icoMobile" viewBox="0 0 11 16">
                                <g>
                                    <path
                                        d="M8.5,0 C9.88071187,0 11,1.11928813 11,2.5 L11,13.5 C11,14.8807119 9.88071187,16 8.5,16 L2.5,16 C1.11928813,16 0,14.8807119 0,13.5 L0,2.5 C0,1.11928813 1.11928813,0 2.5,0 L8.5,0 Z M8.5,1.5 L2.5,1.5 C1.94771525,1.5 1.5,1.94771525 1.5,2.5 L1.5,13.5 C1.5,14.0522847 1.94771525,14.5 2.5,14.5 L8.5,14.5 C9.05228475,14.5 9.5,14.0522847 9.5,13.5 L9.5,2.5 C9.5,1.94771525 9.05228475,1.5 8.5,1.5 Z M7.5,2.5 L7.5,3.5 L3.5,3.5 L3.5,2.5 L7.5,2.5 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoKakaotalk" viewBox="0 0 34 32">
                                <g>
                                    <path
                                        d="M29.3047306,17.5270857 C29.3480595,17.1892201 29.1497973,16.926064 28.9103945,16.6078236 L26.5947094,13.517747 L28.5523846,11.5050492 C28.6245993,11.420973 28.6909056,11.3462635 28.7513033,11.2784673 C29.0176224,10.9789601 29.1513291,10.8284259 29.1513291,10.600506 C29.1616142,10.1132212 28.7664028,9.84716598 28.3735985,9.83646133 C28.0630752,9.83646133 27.8545279,10.0104119 27.7267297,10.1393138 L24.8626504,13.1821115 L24.8626504,10.5262424 C24.8626504,10.0378426 24.5359336,9.71001261 24.0499067,9.71001261 C23.5783227,9.71001261 23.2358499,10.0532306 23.2358499,10.5262424 L23.2358499,17.3859181 C23.2358499,17.859599 23.5630044,18.1776164 24.0499067,18.1776164 C24.513175,18.1776164 24.8626504,17.8375206 24.8626504,17.3859181 L24.8626504,15.1548899 L25.4469331,14.5476239 L27.5833945,17.515489 C27.8969814,17.9472433 28.0661389,18.1394811 28.366377,18.170926 C28.4086117,18.1753863 28.4510652,18.1773934 28.4932999,18.1773934 C28.6677093,18.1773934 29.2412692,18.1307835 29.3047306,17.5270857 Z M22.5340542,17.3613866 C22.5458711,17.1537609 22.4760636,16.9519336 22.3425758,16.8076438 C22.2027418,16.6566636 22.0003218,16.5768247 21.7569801,16.5768247 L19.5021304,16.5768247 L19.5021304,10.5753054 C19.5021304,10.0416339 19.190513,9.71001261 18.6891678,9.71001261 C18.187385,9.71001261 17.8755487,10.0416339 17.8755487,10.5753054 L17.8755487,17.1678108 C17.8755487,17.7418478 18.1937311,18.0848427 18.7259316,18.0848427 L21.7569801,18.0848427 C22.2484778,18.0848427 22.5239879,17.7135251 22.5340542,17.3613866 Z M16.2866062,18.1782854 C16.7023878,18.1782854 17.0282294,17.8636132 17.0282294,17.4619657 C17.0282294,17.3977378 17.0089721,17.2358299 16.9361009,17.0364558 L14.6484263,10.6741005 C14.4361588,10.0617051 13.9945549,9.71068166 13.4371886,9.71068166 C12.803231,9.71068166 12.3966403,10.2091171 12.2277016,10.6763306 L9.86737465,17.0482755 C9.84308425,17.1109423 9.79297162,17.2420743 9.79297162,17.4120107 C9.79297162,17.8417579 10.1446354,18.1782854 10.5932419,18.1782854 C10.9998327,18.1782854 11.2479887,17.9916231 11.3751303,17.5897525 L11.7394864,16.4693321 L15.1375169,16.4693321 L15.4931196,17.6026873 C15.6189483,17.990062 15.8784836,18.1782854 16.2866062,18.1782854 Z M8.41848491,17.3105395 L8.41848491,11.2925172 L10.1275665,11.2925172 C10.6652378,11.2925172 10.8562786,10.8868554 10.8562786,10.5396232 C10.8562786,10.1734349 10.6006822,9.78427615 10.1275665,9.78427615 L5.08194632,9.78427615 C4.60970586,9.78427615 4.35476604,10.1734349 4.35476604,10.5396232 C4.35476604,10.8868554 4.54515029,11.2925172 5.08194632,11.2925172 L6.79234086,11.2925172 L6.79234086,17.3105395 C6.79234086,17.8453261 7.10373946,18.1776164 7.60508464,18.1776164 C8.10664865,18.1776164 8.41848491,17.8453261 8.41848491,17.3105395 Z M17,0 C26.3887881,0 34,6.12819101 34,13.6870143 C34,21.2462837 26.3887881,27.3735826 17,27.3735826 C15.9566068,27.3735826 14.934878,27.297312 13.943567,27.1525762 L7.05165733,31.8936225 C6.96193602,31.9654329 6.85558345,32 6.74923087,32 C6.6240587,32 6.49910536,31.951383 6.40456974,31.8548181 C6.27305143,31.72101 6.22819077,31.524535 6.2877132,31.343894 L7.89000451,25.2440257 C3.1472485,22.8156305 0,18.5469269 0,13.6870143 C0,6.12819101 7.61121195,0 17,0 Z M12.9863448,11.0123788 C12.9902211,10.9958737 13.0078407,10.9958737 13.0118932,11.0123788 L14,15 L12,15 L12.9863448,11.0123788 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoTalk" viewBox="0 0 22 22">
                                <g>
                                    <path d="M11,1 C5.477,1 1,4.858 1,9.617 C1,13.24 2.462,14.76 4.744,16.339 L4.757,20.759 C4.757,20.957 4.983,21.07 5.142,20.952 L9.034,18.067 C9.67,18.176 10.327,18.233 11,18.233 C16.523,18.233 21,14.376 21,9.617 C21,4.858 16.523,1 11,1 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoTalkclose" viewBox="0 0 14 14">
                                <g transform="translate(8.000000, 8.000000) rotate(-315.000000) translate(-8.000000, -8.000000) translate(0.000000, 0.000000)">
                                    <path d="M8,0 L8,16"></path>
                                    <path d="M0,8 L16,8"></path>
                                </g>
                            </symbol>
                            <symbol id="icoPrev" viewBox="0 0 16 16">
                                <g>
                                    <path
                                        d="M14.0013824,3.25000127 C14.3810775,3.25070114 14.6943521,3.53343293 14.7433397,3.89959941 L14.75,4.00138241 L14.7352721,11.9910248 C14.7345738,12.3698771 14.4530474,12.6827626 14.0877898,12.7326922 L13.9862462,12.7396417 L6.00097282,12.7500013 C5.5867596,12.7505366 5.2505379,12.415186 5.24999999,12.0009728 C5.24950813,11.6212774 5.53125475,11.3071165 5.89726559,11.2569792 L5.99902718,11.2500013 L13.236,11.24 L13.25,3.99861759 C13.2507011,3.61892247 13.5334329,3.30564788 13.8995994,3.25666029 L14.0013824,3.25000127 Z"
                                        transform="translate(9.999999, 8.000001) rotate(135.000000) translate(-9.999999, -8.000001) "></path>
                                </g>
                            </symbol>
                            <symbol id="icoCounsel" viewBox="0 0 24 24">
                                <g>
                                    <path
                                        d="M11.9750594,2 C15.9382872,2 19.1855102,5.07620525 19.484645,8.98132852 L19.4572447,8.98056048 C21.137712,8.98056048 22.5,10.3422998 22.5,12.0220904 C22.5,13.6418885 21.2332807,14.9659475 19.6360296,15.0584571 L19.4572447,15.0636203 L19.3311322,15.0638167 C18.5877985,18.4588551 15.5771621,21 11.9750594,21 L11.9750594,21 L11.9750594,19.9030548 L12.205805,19.8989694 C15.65203,19.7767507 18.4097387,16.9276947 18.4097387,13.429416 L18.4097387,13.429416 L18.4097387,9.57058404 L18.4056759,9.33835007 C18.2841329,5.86995166 15.4508632,3.09694522 11.9750594,3.09694522 C8.42201546,3.09694522 5.54038005,5.99456578 5.54038005,9.57058404 L5.54038005,9.57058404 L5.54038005,15.0636234 L4.44299287,15.0636234 L4.442,15.06 L4.36397036,15.0584571 C2.82587675,14.9693738 1.59428446,13.7382776 1.50516527,12.2008034 L1.5,12.0220904 C1.5,10.3422998 2.86228797,8.98056048 4.54275534,8.98056048 L4.46538855,8.9824424 C4.76399106,5.07679023 8.01145474,2 11.9750594,2 Z M16.0154394,12.9694522 L16.0154394,13.5179248 C16.0154394,15.4866079 14.1811647,17.0580662 11.9750594,17.0580662 C9.76864105,17.0580662 7.93467933,15.4867321 7.93467933,13.5179248 L7.93467933,13.5179248 L7.93467933,12.9694522 L16.0154394,12.9694522 Z M14.8402375,14.0663974 L9.10888361,14.0663974 L9.11501836,14.0893393 C9.41332143,15.1016729 10.4836647,15.8899247 11.7948224,15.9565546 L11.7948224,15.9565546 L11.9750594,15.961121 C13.3673038,15.961121 14.5231637,15.1475792 14.8350839,14.0892909 L14.8350839,14.0892909 L14.8402375,14.0663974 Z M19.507,10.079 L19.5071259,13.429416 L19.5032567,13.6743903 C19.5001722,13.7719 19.495253,13.8689449 19.4885326,13.9654912 L19.4572447,13.9666751 C20.5316418,13.9666751 21.4026128,13.0960549 21.4026128,12.0220904 C21.4026128,10.9969425 20.6090215,10.1570731 19.6024298,10.0828394 L19.507,10.079 Z M4.442,10.08 L4.39757024,10.0828394 C3.39097852,10.1570731 2.59738717,10.9969425 2.59738717,12.0220904 C2.59738717,13.0960549 3.46835817,13.9666751 4.54275534,13.9666751 L4.442,13.962 L4.442,10.08 Z M8.68289786,9.03042162 C9.34406535,9.03042162 9.88004751,9.56618792 9.88004751,10.2270891 C9.88004751,10.8879904 9.34406535,11.4237566 8.68289786,11.4237566 C8.02173037,11.4237566 7.48574822,10.8879904 7.48574822,10.2270891 C7.48574822,9.56618792 8.02173037,9.03042162 8.68289786,9.03042162 Z M15.2672209,9.03042162 C15.9283884,9.03042162 16.4643705,9.56618792 16.4643705,10.2270891 C16.4643705,10.8879904 15.9283884,11.4237566 15.2672209,11.4237566 C14.6060534,11.4237566 14.0700713,10.8879904 14.0700713,10.2270891 C14.0700713,9.56618792 14.6060534,9.03042162 15.2672209,9.03042162 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoBot" viewBox="0 0 24 24">
                                <g>
                                    <path
                                        d="M11.9971069,2 C12.7703056,2 13.3971069,2.62680135 13.3971069,3.4 C13.3971069,4.02407644 12.9887656,4.55277966 12.4246908,4.73350184 L12.4248726,5.90932682 C17.1981648,6.13115793 21,10.0713334 21,14.8994751 L21,19.8994751 L3,19.8994751 L3,14.8994751 C3,10.0713334 6.8018352,6.13115793 11.5751274,5.90932682 L11.5748204,4.73518736 C11.0080066,4.55608598 10.5971069,4.02602837 10.5971069,3.4 C10.5971069,2.62680135 11.2239083,2 11.9971069,2 Z M19.799,16.9 L4.199,16.9 L4.2,18.6994751 L19.8,18.6994751 L19.799,16.9 Z M12,7.0994751 C7.69217895,7.0994751 4.2,10.591654 4.2,14.8994751 L4.199,15.8 L19.799,15.8 L19.8,14.8994751 C19.8,10.591654 16.307821,7.0994751 12,7.0994751 Z M9,11 C9.6627417,11 10.2,11.5372583 10.2,12.2 C10.2,12.8627417 9.6627417,13.4 9,13.4 C8.3372583,13.4 7.8,12.8627417 7.8,12.2 C7.8,11.5372583 8.3372583,11 9,11 Z M15,11 C15.6627417,11 16.2,11.5372583 16.2,12.2 C16.2,12.8627417 15.6627417,13.4 15,13.4 C14.3372583,13.4 13.8,12.8627417 13.8,12.2 C13.8,11.5372583 14.3372583,11 15,11 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoMenu" viewBox="0 0 24 24">
                                <g>
                                    <path d="M22,17 L22,18.2 L2,18.2 L2,17 L22,17 Z M22,12 L22,13.2 L2,13.2 L2,12 L22,12 Z M22,7 L22,8.2 L2,8.2 L2,7 L22,7 Z"></path>
                                </g>
                            </symbol>
                            <symbol id="icoAttachment" viewBox="0 0 22 22">
                                <g>
                                    <path
                                        d="M12.93,21.47 L12.08,20.63 L19.41,13.2 C21.54,11.04 21.54,7.52 19.41,5.36 C18.38,4.32 17.01,3.74 15.56,3.74 C14.11,3.74 12.74,4.32 11.71,5.36 L3.83,13.36 C2.37,14.84 2.37,17.24 3.83,18.71 C5.23,20.13 7.68,20.13 9.08,18.71 L16.74,10.94 C17.51,10.15 17.51,8.88 16.74,8.09 C15.99,7.33 14.7,7.33 13.96,8.09 L6.85,15.3 L6,14.46 L13.11,7.25 C14.31,6.03 16.4,6.03 17.6,7.25 C18.83,8.5 18.83,10.53 17.6,11.78 L9.94,19.55 C9.01,20.49 7.77,21.01 6.46,21.01 C5.14,21.01 3.91,20.49 2.98,19.55 C1.07,17.61 1.07,14.45 2.98,12.51 L10.86,4.51 C12.12,3.24 13.79,2.53 15.56,2.53 C17.34,2.53 19.01,3.23 20.27,4.51 C22.86,7.13 22.86,11.41 20.27,14.03 L12.93,21.47 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoThumbsup" viewBox="0 0 22 22">
                                <g>
                                    <path
                                        d="M21.04,10.4417634 L21.04,10.2217634 C21.04,9.05176339 20.09,8.10176339 18.92,8.10176339 L13.28,8.10176339 L13.28,5.57176339 C13.28,3.29176339 11.32,1.98176339 10.57,1.67176339 C9.95,1.42176339 9.3,1.47176339 8.78,1.82176339 C8.29,2.15176339 7.99,2.70176339 7.99,3.30176339 C7.99,3.49176339 8.03,3.79176339 8.07,4.16176339 C8.23,5.38176339 8.5,7.43176339 7.6,8.77176339 C7.51,8.91176339 7.44,9.03176339 7.35,9.16176339 L6.98,9.16176339 C3.74,9.16176339 1.88,11.2017634 1.88,14.7617634 C1.88,18.3217634 3.74,20.3617634 6.98,20.3617634 L10.03,20.3617634 C10.62,20.6217634 11.11,20.7617634 11.35,20.8217634 C11.47,20.8517634 11.6,20.8617634 11.72,20.8617634 L16.78,20.8617634 C17.95,20.8617634 18.9,20.0117634 18.9,18.9717634 L18.9,18.7717634 C18.9,18.4617634 18.82,18.1717634 18.67,17.9117634 C19.39,17.6117634 19.9,16.9517634 19.9,16.2017634 L19.9,16.0017634 C19.9,15.6517634 19.79,15.3217634 19.6,15.0417634 C20.21,14.7117634 20.61,14.1117634 20.61,13.4317634 L20.61,13.2317634 C20.61,12.8117634 20.46,12.4217634 20.19,12.1117634 C20.72,11.7317634 21.04,11.1217634 21.04,10.4417634 Z M7,19.1717634 C4.41,19.1717634 3.1,17.6917634 3.1,14.7717634 C3.1,11.9717634 4.32,10.5117634 6.69,10.3917634 C5.98,11.9017634 5.9,13.0417634 5.9,14.0217634 C5.9,16.5317634 6.95,18.1417634 8.14,19.1617634 L7,19.1617634 L7,19.1717634 Z M19.84,10.4417634 C19.84,10.9417634 19.44,11.3417634 18.94,11.3417634 L17.8,11.3417634 L17.8,12.5417634 L18.52,12.5417634 C19.02,12.5417634 19.44,12.8617634 19.44,13.2317634 L19.44,13.4317634 C19.44,13.8017634 19.02,14.1217634 18.52,14.1217634 L16.81,14.1217634 L16.81,15.3217634 L17.8,15.3217634 C18.3,15.3217634 18.72,15.6417634 18.72,16.0117634 L18.72,16.2117634 C18.72,16.5817634 18.3,16.9017634 17.8,16.9017634 L16.03,16.9017634 L16.03,18.1017634 L16.81,18.1017634 C17.31,18.1017634 17.73,18.4217634 17.73,18.7917634 L17.73,18.9917634 C17.73,19.3617634 17.31,19.6817634 16.81,19.6817634 L11.65,19.6717634 C11.42,19.6217634 10.93,19.4817634 10.35,19.2017634 L10.35,19.1817634 L10.32,19.1817634 C8.95,18.5117634 7.11,17.0617634 7.11,14.0417634 C7.11,12.8617634 7.23,11.5417634 8.62,9.46176339 C9.77,7.75176339 9.45,5.33176339 9.28,4.03176339 C9.24,3.73176339 9.21,3.48176339 9.21,3.32176339 C9.21,3.12176339 9.3,2.95176339 9.46,2.84176339 C9.56,2.77176339 9.68,2.74176339 9.8,2.74176339 C9.9,2.74176339 10.01,2.76176339 10.12,2.81176339 C10.63,3.02176339 12.09,3.99176339 12.09,5.60176339 L12.09,9.33176339 L18.93,9.33176339 C19.43,9.33176339 19.85,9.74176339 19.85,10.2517634 L19.85,10.4417634 L19.84,10.4417634 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoBookmark" viewBox="0 0 24 24">
                                <g>
                                    <path d="M6,5 L6,22 L6,22 L12,16 L18,22 L18,5 C18,3.8954305 17.1045695,3 16,3 L8,3 C6.8954305,3 6,3.8954305 6,5 Z M9,4 L15,4 C16.1045695,4 17,4.8954305 17,6 L17,19.827 L17,19.827 L12,14.683 L7,19.827 L7,6 C7,4.8954305 7.8954305,4 9,4 Z"></path>
                                </g>
                            </symbol>
                            <symbol id="icoSending" viewBox="0 0 12 10">
                                <g>
                                    <path
                                        d="M11.9119006,6.37336527 C12.2111355,6.3248825 12.3346371,6.11107198 12.3500235,5.99804022 L12.8333333,2.67520503 C12.8333333,2.42139123 12.5150985,2.25631072 12.2446252,2.3698197 L1.9393459,6.69461467 C1.8131153,6.79640978 1.75,6.89820489 1.75,7 L1.75757384,7.06107707 C1.77272151,7.12215413 1.81059069,7.1832312 1.87118138,7.24430827 L1.9393459,7.30538533 L12.2446252,11.6301803 C12.49051,11.7333703 12.7758672,11.606321 12.8257182,11.3916743 L12.8333333,11.324795 L12.3500235,8.00975711 C12.3365604,7.91085432 12.2403216,7.73479279 12.0160083,7.65984309 L11.267446,7.5076707 C10.586558,7.37922662 9.39727493,7.17966471 7.76349697,7.02651981 L7.47058208,7 L8.04718359,6.94611872 C10.3725709,6.71446345 11.7285513,6.40307198 11.9119006,6.37336527 Z"
                                        transform="translate(-2.000000, -2.000000)"></path>
                                </g>
                            </symbol>
                            <symbol id="icoTimer" viewBox="0 0 48 48">
                                <g>
                                    <circle cx="24" cy="24" r="23"></circle>
                                </g>
                            </symbol>
                            <symbol id="icoKakao" viewBox="0 0 22 7">
                                <g>
                                    <path
                                        d="M11.8117749,2.22048479 L12.4108611,2.65295381 L10.9386076,4.5000719 L12.6437961,6.54672405 L12.0533263,7.00446158 L10.0399782,4.54150838 L11.8117749,2.22048479 Z M2.81235564,2.22047511 L3.4114419,2.65304095 L1.9386075,4.50006222 L3.64437686,6.54671437 L3.05342299,7.00445189 L1.04007493,4.5414987 L2.81235564,2.22047511 Z M19.9763899,2.26188254 C20.6084898,2.26188254 21.1052434,2.46722546 21.4653922,2.87752403 C21.826122,3.28811304 22.0065836,3.87606567 22.0065836,4.64147872 C22.0065836,5.39566132 21.8277678,5.97557837 21.4697489,6.38045534 C21.1122141,6.78504188 20.6139114,6.98767399 19.9763899,6.98767399 C19.34429,6.98767399 18.8475363,6.78504188 18.4873875,6.38045534 C18.1266578,5.97557837 17.9461961,5.39566132 17.9461961,4.64147872 C17.9461961,3.87606567 18.1277228,3.28811304 18.4911633,2.87752403 C18.8546038,2.46722546 19.3497116,2.26188254 19.9763899,2.26188254 Z M6.11626113,2.25354684 C7.19254457,2.25354684 7.73044425,2.82765503 7.73044425,3.97577461 L7.73044425,6.88775206 L7.16495252,6.88775206 L7.07336629,6.38857806 C6.84585293,6.5716537 6.60323655,6.71300243 6.34542034,6.8130115 C6.08760413,6.91292375 5.84218013,6.96278306 5.6087611,6.96278306 C5.20407775,6.96278306 4.88672081,6.84767098 4.65649665,6.61744682 C4.42627249,6.38722266 4.31086996,6.0697689 4.31086996,5.66489192 C4.31086996,5.20454041 4.46470772,4.85349213 4.77296413,4.61252159 C5.08063965,4.3711638 5.52859895,4.25033968 6.11626113,4.25033968 L6.99862573,4.25033968 L6.99862573,3.95921938 C6.99862573,3.25479928 6.68775534,2.90268604 6.06640182,2.90268604 C5.86706138,2.90268604 5.65745864,2.9303749 5.43865856,2.98584943 C5.21927758,3.04132397 5.01829131,3.11073975 4.83521566,3.19380633 L4.61041309,2.65300222 C4.83792646,2.52540111 5.08335045,2.4271347 5.34707233,2.35752529 C5.61040694,2.28849677 5.86706138,2.25354684 6.11626113,2.25354684 Z M15.2828472,2.25354684 C16.3585498,2.25354684 16.8970304,2.82765503 16.8970304,3.97577461 L16.8970304,6.88775206 L16.3309577,6.88775206 L16.2394683,6.38857806 C16.011955,6.5716537 15.7698227,6.71300243 15.5114256,6.8130115 C15.2536094,6.91292375 15.0081854,6.96278306 14.7753472,6.96278306 C14.3701798,6.96278306 14.052726,6.84767098 13.8225019,6.61744682 C13.5922777,6.38722266 13.4774561,6.0697689 13.4774561,5.66489192 C13.4774561,5.20454041 13.6312938,4.85349213 13.9389694,4.61252159 C14.2472258,4.3711638 14.6946042,4.25033968 15.2828472,4.25033968 L16.1647278,4.25033968 L16.1647278,3.95921938 C16.1647278,3.25479928 15.8543415,2.90268604 15.2329879,2.90268604 C15.0331634,2.90268604 14.8240448,2.9303749 14.6046638,2.98584943 C14.3852828,3.04132397 14.1843933,3.11073975 14.0018018,3.19380633 L13.7769992,2.65300222 C14.0045126,2.52540111 14.2499366,2.4271347 14.5131744,2.35752529 C14.7764122,2.28849677 15.0331634,2.25354684 15.2828472,2.25354684 Z M9.76541317,0.290009681 L9.76541317,6.88770365 L9.00000012,6.88770365 L9.00000012,0.456530102 L9.76541317,0.290009681 Z M0.76541305,0.29 L0.76541305,6.88769397 L-6.62803146e-13,6.88769397 L-6.62803146e-13,0.456617235 L0.76541305,0.29 Z M19.9763899,2.87752403 C19.5772249,2.87752403 19.2706144,3.02729559 19.0571391,3.32683872 C18.8432765,3.62638185 18.7364904,4.06456291 18.7364904,4.64147872 C18.7364904,5.21287611 18.8432765,5.64408655 19.0571391,5.93520685 C19.2706144,6.22632714 19.5772249,6.37203251 19.9763899,6.37203251 C20.3809764,6.37203251 20.6902978,6.22632714 20.9042572,5.93520685 C21.1176356,5.64408655 21.2244217,5.21287611 21.2244217,4.64147872 C21.2244217,4.06456291 21.1176356,3.62638185 20.9042572,3.32683872 C20.6902978,3.02729559 20.3809764,2.87752403 19.9763899,2.87752403 Z M6.99862573,4.76626254 L6.20290984,4.76626254 C5.79996914,4.76626254 5.50584761,4.83567832 5.32054524,4.97431625 C5.13582375,5.11295418 5.04326937,5.33204471 5.04326937,5.63158784 C5.04326937,6.10849458 5.27775336,6.34714158 5.74739903,6.34714158 C5.85244244,6.34714158 5.96135841,6.33329715 6.07453421,6.30541466 C6.18780682,6.27782261 6.30098262,6.24180773 6.41415842,6.19737001 C6.52743103,6.1529323 6.63412028,6.09881316 6.73325801,6.03510942 C6.83287982,5.97121205 6.92117437,5.90324848 6.99862573,5.83121872 L6.99862573,4.76626254 Z M16.1647278,4.76626254 L15.3694959,4.76626254 C14.9659744,4.76626254 14.6718528,4.83567832 14.4871313,4.97431625 C14.3019258,5.11295418 14.2098555,5.33204471 14.2098555,5.63158784 C14.2098555,6.10849458 14.4443395,6.34714158 14.9139851,6.34714158 C15.0185445,6.34714158 15.1279445,6.33329715 15.2411203,6.30541466 C15.3543929,6.27782261 15.4675687,6.24180773 15.5807445,6.19737001 C15.6940171,6.1529323 15.8001255,6.09881316 15.8998441,6.03510942 C15.998885,5.97121205 16.0871796,5.90324848 16.1647278,5.83121872 L16.1647278,4.76626254 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoSpinner" viewBox="0 0 30 30">
                                <g fill="none" stroke-width="2" transform="translate(1 1)">
                                    <circle cx="14" cy="14" r="14" stroke="#e6e6e6"></circle>
                                    <path d="M14 0C6.268 0 0 6.268 0 14" stroke="#8a8a8a"></path>
                                </g>
                            </symbol>
                            <symbol id="icoChannel" viewBox="0 0 20 16">
                                <g>
                                    <path
                                        d="M7.4959378,6.39488462e-14 C11.620176,6.39488462e-14 14.9918756,2.92608556 14.9918756,6.57602161 C14.9918756,10.2258177 11.6200955,13.1520432 7.4959378,13.1520432 C7.16831007,13.1520432 6.84254444,13.133372 6.52004239,13.0965129 L6.19868011,13.053609 L3.77778611,14.7409153 C3.3227098,15.0584935 2.68191862,14.7878311 2.60810608,14.2507173 L2.60109427,14.1469645 L2.60109427,11.557093 C0.80210055,10.2164139 0,8.85110377 0,6.57602161 C0,2.92608556 3.37169965,6.39488462e-14 7.4959378,6.39488462e-14 Z M7.4959378,1 C3.88379469,1 1,3.5214428 1,6.57602161 C1,8.37759822 1.5371141,9.45755439 2.99421413,10.599138 L3.19864794,10.7552641 L3.60109427,11.0551825 L3.601,13.644 L5.95472547,12.0047154 L6.34975323,12.0650864 C6.72813152,12.1229129 7.1111697,12.1520432 7.4959378,12.1520432 C11.1079715,12.1520432 13.9918756,9.6304863 13.9918756,6.57602161 C13.9918756,3.5214428 11.1080809,1 7.4959378,1 Z M5.40227529,4.29368006 C6.34068589,4.29368006 7.14098107,4.85648452 7.4376813,5.7109669 L7.48732186,5.87453425 L6.43162592,6.14668136 C6.31052238,5.68281043 5.90625004,5.37744479 5.40227529,5.37744479 C4.67091249,5.37744479 4.18093236,5.8949217 4.18093236,6.70161177 C4.18093236,7.44589127 4.71918267,8.00944485 5.40227529,8.00944485 C5.83940529,8.00944485 6.21358868,7.76658289 6.38026953,7.39007308 L6.42390416,7.27321992 L7.46688657,7.59009561 C7.18979856,8.49065218 6.36001901,9.09320958 5.40227529,9.09320958 C4.10372091,9.09320958 3.09028989,8.03213693 3.09028989,6.70161177 C3.09028989,5.3106386 4.05321108,4.29368006 5.40227529,4.29368006 Z M18,4 L17.999,6 L20,6 L20,7 L17.999,7 L18,9 L17,9 L16.999,7 L15,7 L15,6 L16.999,6 L17,4 L18,4 Z M9.2222085,3.79457112 L9.22162178,5.2585347 C9.41432277,5.19865644 9.6203415,5.16632179 9.83355645,5.16632179 C10.8145306,5.16632179 11.6431042,5.85047581 11.7235092,6.75257736 L11.7299004,6.89675768 L11.7299004,8.79323898 L10.5756795,8.79323898 L10.5756795,6.89675768 C10.5756795,6.59038761 10.2581019,6.31166406 9.83355645,6.31166406 C9.44780932,6.31166406 9.15030054,6.54202651 9.09939603,6.81407968 L9.09168117,6.89675768 L9.09168117,8.79323898 L7.93746028,8.79323898 L7.93746028,3.79457112 L9.2222085,3.79457112 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoChannel2" viewBox="0 0 31 22">
                                <g>
                                    <path
                                        d="M10.1115987,-3.55271368e-15 C15.7361755,-3.55271368e-15 20.16,4.22018543 20.16,9.46344613 C20.16,14.7067068 15.6097806,18.9268923 10.0484013,18.9268923 C9.41642633,18.9268923 8.72125392,18.86295 8.089279,18.7350656 L8.089279,18.7350656 L8.0260815,18.6711234 L4.17103448,21.5485226 C4.0446395,21.676407 3.79184953,21.5485226 3.79184953,21.356696 L3.79184953,21.356696 L3.79184953,16.8167995 L3.59253396,16.6650851 C1.48563434,15.0400988 2.48689958e-14,13.1837198 2.48689958e-14,9.46344613 C2.48689958e-14,4.22018543 4.55021944,-3.55271368e-15 10.1115987,-3.55271368e-15 Z M6.76213166,5.62691391 C4.67661442,5.62691391 2.97028213,7.225469 2.97028213,9.46344613 C2.97028213,11.7014232 4.61341693,13.2999783 6.76213166,13.2999783 C8.59485893,13.2999783 9.92200627,12.1490187 10.3011912,10.358637 L10.3011912,10.358637 L8.8476489,10.358637 C8.59485893,11.31777 7.77329154,11.8932499 6.76213166,11.8932499 C5.43498433,11.8932499 4.42382445,10.8701746 4.42382445,9.46344613 C4.42382445,8.05671765 5.37178683,7.03364239 6.82532915,7.03364239 C7.83648903,7.03364239 8.65805643,7.67306443 8.91084639,8.63219748 L8.91084639,8.63219748 L10.3643887,8.63219748 C9.98520376,6.84181578 8.59485893,5.62691391 6.76213166,5.62691391 Z M12.9554859,5.62691391 L11.6283386,5.62691391 L11.6283386,13.1081517 L12.9554859,13.1081517 L12.9554859,10.2946948 C12.9554859,9.46344613 13.3978683,9.0158507 14.0930408,9.0158507 C14.7250157,9.0158507 15.1042006,9.39950392 15.1042006,10.1028682 L15.1042006,10.1028682 L15.1042006,13.1720939 L16.4945455,13.1720939 L16.4945455,9.84709935 C16.4945455,9.14373511 16.304953,8.63219748 15.925768,8.24854426 C15.5465831,7.86489104 15.1042006,7.67306443 14.5354232,7.67306443 C13.7770533,7.67306443 13.2714734,7.92883324 12.9554859,8.44037087 L12.9554859,8.44037087 L12.9554859,5.62691391 Z M27.1938462,5.04 L27.193,8.086 L30.24,8.08615385 L30.24,9.91384615 L27.193,9.913 L27.1938462,12.96 L25.3661538,12.96 L25.366,9.913 L22.32,9.91384615 L22.32,8.08615385 L25.366,8.086 L25.3661538,5.04 L27.1938462,5.04 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoComplete" viewBox="0 0 63 63">
                                <g>
                                    <circle fill-opacity="0.65" fill="#424242" cx="31.5" cy="31.5" r="31.5"></circle>
                                    <path d="M41.9959358,24.5 L43.4101494,25.9142136 L29.2680138,40.0563492 L27.8538002,38.6421356 L27.902,38.594 L21.5,32.1920509 L22.9142136,30.7778374 L29.316,37.179 L41.9959358,24.5 Z" fill="#FFFFFF"></path>
                                </g>
                            </symbol>
                            <symbol id="icoReply" viewBox="0 0 28 28">
                                <g transform="translate(3.000000, 1.000000)">
                                    <path
                                        d="M3.3,0 L3.3,12 C3.3,14.7982427 5.51025922,17.0802518 8.28018869,17.1954381 L8.5,17.2 L17.966,17.2 L12.6924499,13.0187555 L14.3075501,10.9812445 L21.5189353,16.6975864 C22.5143808,17.4866591 22.6816791,18.9332969 21.8926064,19.9287425 C21.8194153,20.0210759 21.7392919,20.1075801 21.6529715,20.1875197 L21.5189353,20.3024136 L14.3075501,26.0187555 L12.6924499,23.9812445 L17.966,19.8 L8.5,19.8 C4.27502166,19.8 0.834616218,16.4408441 0.703855423,12.2476042 L0.7,12 L0.7,0 L3.3,0 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoWarning" viewBox="0 0 40 33">
                                <g>
                                    <path
                                        d="M21.2860505,0.715394265 C21.6379245,0.926518671 21.932419,1.22101318 22.1435434,1.57288719 L38.7280675,29.2137606 C39.4384379,30.3977113 39.0545252,31.9333619 37.8705745,32.6437323 C37.482036,32.8768554 37.037445,33 36.5843351,33 L3.41528704,33 C2.03457516,33 0.915287037,31.8807119 0.915287037,30.5 C0.915287037,30.0468901 1.03843162,29.6022991 1.27155472,29.2137606 L17.8560788,1.57288719 C18.5664492,0.388936526 20.1020998,0.00502386582 21.2860505,0.715394265 Z M19.6242129,2.52895559 L19.5710646,2.6018787 L2.98654057,30.2427521 C2.93991595,30.3204598 2.91528704,30.409378 2.91528704,30.5 C2.91528704,30.7454599 3.0921622,30.9496084 3.32541141,30.9919443 L3.41528704,31 L36.5843351,31 C36.6749571,31 36.7638753,30.9753711 36.841583,30.9287465 C37.0520631,30.8024584 37.1361175,30.5457557 37.0524146,30.3239644 L37.0130816,30.2427521 L20.4285576,2.6018787 C20.4004076,2.55496217 20.364847,2.51314603 20.3234159,2.47797048 L20.257059,2.43038012 C20.0465788,2.30409205 19.7805215,2.35072772 19.6242129,2.52895559 Z M20.1965083,22.9350726 C20.779624,22.9350726 21.2523326,23.4077813 21.2523326,23.9908969 C21.2523326,24.5740126 20.779624,25.0467212 20.1965083,25.0467212 L19.8034917,25.0467212 C19.220376,25.0467212 18.7476674,24.5740126 18.7476674,23.9908969 C18.7476674,23.4077813 19.220376,22.9350726 19.8034917,22.9350726 L20.1965083,22.9350726 Z M20,12.8868912 C20.6363382,12.8868912 21.1521923,13.4027453 21.1521923,14.0390835 L21.1519517,14.062627 L21.019733,20.5319195 C21.008431,21.0849165 20.5569067,21.5273069 20.0037941,21.5273069 C19.4505429,21.5273069 18.9987719,21.0850633 18.9869815,20.5319377 L18.8490804,14.0626054 C18.8355311,13.4269701 19.3398315,12.900702 19.9754669,12.8871527 L20,12.8868912 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoComment" viewBox="0 0 16 16">
                                <g>
                                    <path
                                        d="M9.60286272,2.5 C12.307477,2.5 14.5,4.69252304 14.5,7.39713728 C14.5,10.1017515 12.307477,12.2942746 9.60276264,12.2942746 L9.60276264,12.2942746 L8.417,12.293 L4.90956749,15.31066 L5.496,12.21 L5.40714268,12.1942006 C3.2376997,11.7493609 1.60479066,9.87450171 1.50485244,7.61678594 L1.50485244,7.61678594 L1.5,7.39713728 C1.5,4.69252305 3.69252305,2.5 6.39713728,2.5 L6.39713728,2.5 Z M9.60286272,3.5 L6.39713728,3.5 C4.24480779,3.5 2.5,5.24480779 2.5,7.39713728 C2.5,9.44671688 4.08786734,11.1425437 6.1208839,11.2846553 L6.1208839,11.2846553 L6.68187397,11.3238696 L6.423,12.688 L8.04557953,11.2939629 L9.60286272,11.2942746 C11.7551922,11.2942746 13.5,9.54946678 13.5,7.39713728 C13.5,5.24480779 11.7551922,3.5 9.60286272,3.5 L9.60286272,3.5 Z M9,8 L9,9 L5,9 L5,8 L9,8 Z M11,6 L11,7 L5,7 L5,6 L11,6 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoHeart" viewBox="0 0 16 16">
                                <g>
                                    <path
                                        d="M10.2785432,3.00693968 C9.47148672,3.05763127 8.72229678,3.38383619 8.14312321,3.91316511 L8.001,4.051 L7.85725878,3.91245822 C7.22424056,3.33533459 6.39039963,3 5.5,3 C3.56700338,3 2,4.56700338 2,6.5 L2.00648671,6.71403174 C2.07970145,7.91936805 2.76755754,8.98995579 3.80880078,9.56497448 L3.911,9.617 L6.9468555,12.6472978 L7.06371263,12.751605 L7.19033896,12.8408022 C7.79415789,13.2240802 8.56795913,13.146588 9.06814578,12.645625 L12.096,9.613 L12.0130597,9.65681906 C13.2172703,9.07874482 14,7.85979216 14,6.5 C14,4.56700339 12.4329966,3 10.5,3 L10.2785432,3.00693968 Z M10.5,4 C11.8807118,4 13,5.11928814 13,6.5 C13,7.47158488 12.4409863,8.3421423 11.5802963,8.75531154 L11.4429,8.85273671 L8.36054028,11.9390173 C8.18195008,12.1178847 7.89829999,12.1347763 7.70098582,11.9816 L7.63077111,11.9183943 L4.56447419,8.85598823 L4.42628249,8.75845779 C3.56204665,8.34670068 3,7.47420123 3,6.5 C3,5.11928812 4.11928812,4 5.5,4 C6.34854287,4 7.12404269,4.42544906 7.58479572,5.1196894 L8.00247921,5.74903468 L8.41865406,5.11869074 C8.87630122,4.42553227 9.65132046,4 10.5,4 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoShare" viewBox="0 0 16 16">
                                <g>
                                    <path
                                        d="M5.87158181,6.00000001 L5.87158181,7.00000001 L4.49999979,6.99900022 L4.49999979,12.9990002 L11.4999998,12.9990002 L11.4999998,6.99900022 L9.99999979,7.00000001 L9.99999979,6.00000001 L12.4999998,6.00000001 L12.4999998,14 L3.49999979,14 L3.49999979,6.00000001 L5.87158181,6.00000001 Z M8.23223305,2.00000022 L11.0606602,4.82842734 L10.3535534,5.53553412 L8.499,3.68100022 L8.5,10.0000002 L7.5,10.0000002 L7.499,3.74300022 L5.70710678,5.53553412 L5,4.82842734 L7.82842712,2.00000022 L8.03,2.20200022 L8.23223305,2.00000022 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoSubscriber" viewBox="0 0 16 16">
                                <g>
                                    <path
                                        d="M8,3 C9.65685425,3 11,4.34314575 11,6 C11,6.82645468 10.6658106,7.57485525 10.1251946,8.11743901 C10.7750424,8.37559546 11.3184015,8.77300182 11.75,9.31249999 C12.4772806,10.2216007 12.8751709,11.4948162 12.975198,13.1433905 L12.975198,13.1433905 L13.0158332,14 L2.99083788,14 L3.00874709,13.4827001 C3.07145329,11.6714577 3.47268581,10.2841427 4.25,9.31249999 C4.68143628,8.77320465 5.22454908,8.3758943 5.87344044,8.11688514 C5.33418936,7.57485525 5,6.82645468 5,6 C5,4.34314575 6.34314575,3 8,3 Z M8.99136544,8.83134523 L8.85172825,8.87737216 C8.5817302,8.9571701 8.29586683,9 8,9 C7.65235647,9 7.31852398,8.94086797 7.00801182,8.83211322 C6.15140531,8.98431608 5.49885375,9.35221387 5.03086881,9.93719504 C4.49014694,10.6130974 4.16048406,11.5937887 4.04580026,12.8943001 L4.04580026,12.8943001 L4.037,13 L11.961,13 L11.9539661,12.8917562 C11.847866,11.6920343 11.5588392,10.7651195 11.0900671,10.0984484 L11.0900671,10.0984484 L10.9691312,9.93719505 C10.5009791,9.35200495 9.84812856,8.98405332 8.99136544,8.83134523 Z M8,4 C6.8954305,4 6,4.8954305 6,6 C6,6.7937599 6.46240668,7.47951893 7.13253881,7.80259587 C7.40874,7.76725583 7.69795798,7.75 8,7.75 C8.30208695,7.75 8.59134605,7.76726096 8.86750708,7.80195166 C9.53768245,7.47938674 10,6.79368339 10,6 C10,4.8954305 9.1045695,4 8,4 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoViewcount" viewBox="0 0 16 16">
                                <g>
                                    <path
                                        d="M8,3.5 C10.0553785,3.5 11.864587,4.94736682 13.4363192,7.75581655 L13.4363192,7.75581655 L13.572975,8 L13.4363192,8.24418345 C11.864587,11.0526332 10.0553785,12.5 8,12.5 C5.94462154,12.5 4.13541302,11.0526332 2.5636808,8.24418345 L2.5636808,8.24418345 L2.42702498,8 L2.5636808,7.75581655 C4.13541302,4.94736682 5.94462154,3.5 8,3.5 Z M8,4.5 C6.49396307,4.5 5.07571343,5.54535309 3.75215231,7.70455422 L3.75215231,7.70455422 L3.576,8 L3.75877091,8.3062325 C5.0274861,10.371909 6.38315294,11.4147292 7.81969739,11.4949779 L7.81969739,11.4949779 L8,11.5 C9.50603693,11.5 10.9242866,10.4546469 12.2478477,8.29544578 L12.2478477,8.29544578 L12.423,8 L12.2412291,7.6937675 C10.9725139,5.62809102 9.61684706,4.58527084 8.18030261,4.50502208 L8.18030261,4.50502208 Z M8,6 C9.1045695,6 10,6.8954305 10,8 C10,9.1045695 9.1045695,10 8,10 C6.8954305,10 6,9.1045695 6,8 C6,6.8954305 6.8954305,6 8,6 Z M8,7 C7.44771525,7 7,7.44771525 7,8 C7,8.55228475 7.44771525,9 8,9 C8.55228475,9 9,8.55228475 9,8 C9,7.44771525 8.55228475,7 8,7 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoHome" viewBox="0 0 24 24">
                                <g>
                                    <path
                                        d="M12,2.43429107 L23.921396,12.5851006 L23.078604,13.5748994 L20.149604,11.0802911 L20.15,20.462 C20.15,20.94304 19.7878943,21.3395057 19.3213906,21.3936894 L19.212,21.4 L4.788,21.4 C4.30695998,21.4 3.91049428,21.0378943 3.85631061,20.5713906 L3.85,20.462 L3.84960396,11.0802911 L0.921396044,13.5748994 L0.0786039558,12.5851006 L12,2.43429107 Z M12,4.141 L5.14960396,9.97329107 L5.15,20.1 L18.85,20.1 L18.849604,9.97329107 L12,4.141 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoManage" viewBox="0 0 15 12">
                                <g>
                                    <path
                                        d="M5.5,7 C6.65979797,7 7.63513535,7.7897697 7.91755248,8.86084946 L7.9501074,9.00057405 L7.9501074,9.00057405 L14.5,9 C14.7761424,9 15,9.22385763 15,9.5 C15,9.77614237 14.7761424,10 14.5,10 L7.94990271,10.0004345 L7.91755248,10.1391505 C7.63513535,11.2102303 6.65979797,12 5.5,12 C4.34020203,12 3.36486465,11.2102303 3.08244752,10.1391505 L3.05009729,10.0004345 L3.05009729,10.0004345 L0.5,10 C0.223857625,10 3.38176876e-17,9.77614237 0,9.5 C-3.38176876e-17,9.22385763 0.223857625,9 0.5,9 L3.0498926,9.00057405 L3.08244752,8.86084946 C3.36486465,7.7897697 4.34020203,7 5.5,7 Z M5.5,8 C4.67157288,8 4,8.67157288 4,9.5 C4,10.3284271 4.67157288,11 5.5,11 C6.32842712,11 7,10.3284271 7,9.5 C7,8.67157288 6.32842712,8 5.5,8 Z M9.5,0 C10.659798,0 11.6351354,0.789769701 11.9175525,1.86084946 L11.9500875,2.00047581 L11.9500875,2.00047581 L14.5,2 C14.7761424,2 15,2.22385763 15,2.5 C15,2.77614237 14.7761424,3 14.5,3 L11.9499027,3.00043449 L11.9175525,3.13915054 C11.6351354,4.2102303 10.659798,5 9.5,5 C8.34020203,5 7.36486465,4.2102303 7.08244752,3.13915054 L7.05009729,3.00043449 L7.05009729,3.00043449 L0.5,3 C0.223857625,3 3.38176876e-17,2.77614237 0,2.5 C-3.38176876e-17,2.22385763 0.223857625,2 0.5,2 L7.04991252,2.00047581 L7.08244752,1.86084946 C7.36486465,0.789769701 8.34020203,0 9.5,0 Z M9.5,1 C8.67157288,1 8,1.67157288 8,2.5 C8,3.32842712 8.67157288,4 9.5,4 C10.3284271,4 11,3.32842712 11,2.5 C11,1.67157288 10.3284271,1 9.5,1 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoCheckScc" viewBox="0 0 16 16">
                                <g>
                                    <polygon points="11.3390625 4 6.8125 8.6146875 4.87153365 6.96528663 3.51765397 8 6.8125 10.9375 12.5 5.1609375"></polygon>
                                </g>
                            </symbol>
                            <symbol id="icoWarningScc" viewBox="0 0 35 35">
                                <g>
                                    <path
                                        d="M17.5,2 C26.0467,2 33,8.9533 33,17.5 C33,26.0467 26.0467,33 17.5,33 C8.9533,33 2,26.0467 2,17.5 C2,8.9533 8.9533,2 17.5,2 Z M17.5,0 C7.835625,0 0,7.835625 0,17.5 C0,27.164375 7.835625,35 17.5,35 C27.164375,35 35,27.164375 35,17.5 C35,7.835625 27.164375,0 17.5,0 Z M16.3610562,8.01207494 L18.7032237,8.01863007 L18.6970597,19.9940928 L16.3717847,19.9804349 L16.3610562,8.01207494 Z M17.5,26 C16.672,26 16,25.328 16,24.5 C16,23.672 16.672,23 17.5,23 C18.328,23 19,23.672 19,24.5 C19,25.328 18.328,26 17.5,26 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoWarningScc2" viewBox="0 0 24 24">
                                <g>
                                    <path
                                        d="M10.7260537,4.00851558 L3.26359336,17.0758646 C2.71582777,18.0350448 3.0493452,19.2566657 4.00852539,19.8044313 C4.30998326,19.9765869 4.65106057,20.067311 4.99821221,20.0676808 L20.0240067,20.0836872 C21.1285755,20.0848638 22.0249594,19.1903877 22.026136,18.0858188 C22.0265112,17.7336479 21.9338887,17.3876218 21.7576344,17.0827301 L14.1943003,3.99937471 C13.6414864,3.04309519 12.4181244,2.71602173 11.4618449,3.26883569 C11.155458,3.44595434 10.9015549,3.70119934 10.7260537,4.00851558 Z M11.5039851,7.16554927 L13.3802277,7.16350426 L13.3386715,13.9215042 L11.5323086,13.9141291 L11.5039851,7.16554927 Z M12.4480309,17.1251894 C11.8960309,17.1251894 11.3420589,16.5986063 11.3420589,16.0466063 C11.3420589,15.4946063 11.88353,14.9216392 12.43553,14.9216392 C12.98753,14.9216392 13.5431117,15.4626401 13.5431117,16.0146401 C13.5431117,16.5666401 13.0000309,17.1251894 12.4480309,17.1251894 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoCall" viewBox="0 0 24 24">
                                <g>
                                    <path
                                        d="M9.01977386,2.61407487 C6.43280742,3.64319178 5.1314239,4.73352156 4.93810315,6.5463774 C4.64452689,9.29354501 5.28423374,12.0458471 6.71160711,14.7310999 L6.86334387,15.003214 C8.40015002,17.6377318 10.4038776,19.6295546 12.8946918,20.8243278 C14.5377645,21.6136471 16.1487465,21.0811574 18.3861921,19.4227863 C18.8554126,19.0740418 18.9374016,18.4027262 18.5621939,17.9546933 L15.9972473,14.8877006 C15.6772801,14.5059571 15.1281081,14.4112885 14.700247,14.6648358 L13.1154035,15.5973202 C13.0333446,15.6455297 12.9310761,15.6358818 12.8681772,15.5776078 C12.0822388,14.8505318 11.3799126,13.9036836 10.6786117,12.6952211 C10.0274399,11.4755008 9.59167616,10.3797955 9.38700566,9.33075557 C9.37015133,9.24523169 9.41549131,9.15349507 9.49889221,9.10976045 L11.1278101,8.25112198 C11.5678429,8.01844317 11.7751846,7.50267466 11.6184885,7.03100354 L10.3609817,3.23640428 C10.177547,2.68135579 9.5630126,2.39867991 9.01977386,2.61407487 Z M9.31464214,3.35775 C9.43213082,3.31116556 9.56303251,3.37137822 9.60149132,3.48774928 L10.8591943,7.28294059 C10.8926947,7.38378052 10.8484276,7.49389636 10.7543083,7.54366449 L9.12660589,8.40166288 C8.73379319,8.60764899 8.51596704,9.04837776 8.60195692,9.4846968 C8.82400239,10.622796 9.28745158,11.7881148 9.97981935,13.0844386 C10.7246374,14.3683844 11.4717062,15.3755526 12.3246945,16.1646568 C12.6497336,16.4657961 13.1380479,16.5118635 13.5208676,16.2869569 L15.1070125,15.3537047 C15.1983987,15.2995522 15.3155241,15.3197428 15.3838506,15.401261 L17.9486887,18.4681242 C18.0276755,18.562442 18.0102074,18.7054687 17.9093985,18.7803942 C15.8886169,20.2781758 14.5359874,20.7252704 13.2408953,20.1031184 C10.9045412,18.9824352 9.01508381,17.1042037 7.55815448,14.6067553 L7.41411213,14.3484509 C6.06146286,11.8035964 5.45820951,9.20813332 5.73358335,6.63129645 C5.88594584,5.20252476 6.97865844,4.28702439 9.31464214,3.35775 Z"
                                        transform="translate(11.833238, 11.862488) rotate(-3.000000) translate(-11.833238, -11.862488) "></path>
                                </g>
                            </symbol>
                            <symbol id="icoApp" viewBox="0 0 24 24">
                                <g>
                                    <path
                                        d="M20.7,19.9603162 L20.7,20.7603162 L3.1,20.7603162 L3.1,19.9603162 L20.7,19.9603162 Z M12.3065371,3.1 L12.306,14.384 L16.514848,10.1756189 L17.0805577,10.7412801 L11.906579,15.915702 L6.73260041,10.7412801 L7.29831007,10.1756189 L11.506,14.384 L11.5065371,3.1 L12.3065371,3.1 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoQr" viewBox="0 0 24 24">
                                <g>
                                    <path
                                        d="M19.9,15.9 L19.9,19.9 L15.9,19.9 L15.9,18.94 L18.94,18.94 L18.94,15.9 L19.9,15.9 Z M4.86,15.9 L4.86,18.94 L7.9,18.94 L7.9,19.9 L3.9,19.9 L3.9,15.9 L4.86,15.9 Z M19.9,11.42 L19.9,12.22 L3.9,12.22 L3.9,11.42 L19.9,11.42 Z M7.9,3.9 L7.9,4.86 L4.86,4.86 L4.86,7.9 L3.9,7.9 L3.9,3.9 L7.9,3.9 Z M19.9,3.9 L19.9,7.9 L18.94,7.9 L18.94,4.86 L15.9,4.86 L15.9,3.9 L19.9,3.9 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoFaq" viewBox="0 0 24 24">
                                <g>
                                    <path
                                        d="M11.9,1.9 C17.4228163,1.9 21.9,6.37721807 21.9,11.8998065 C21.9,17.4227196 17.4228787,21.9 11.9,21.9 C6.37712133,21.9 1.9,17.4227196 1.9,11.8998065 C1.9,6.37721807 6.37718365,1.9 11.9,1.9 Z M11.9,2.7 C6.81901283,2.7 2.7,6.8190445 2.7,11.8998065 C2.7,16.9808982 6.8189555,21.1 11.9,21.1 C16.9810445,21.1 21.1,16.9808982 21.1,11.8998065 C21.1,6.8190445 16.9809872,2.7 11.9,2.7 Z M12.3,10.3 L12.3,16.7 L11.5,16.7 L11.5,10.3 L12.3,10.3 Z M11.9003267,7.1 C12.3419763,7.1 12.7,7.45103707 12.7,7.88399347 C12.7,8.31662986 12.3419763,8.66734694 11.9003267,8.66734694 C11.458677,8.66734694 11.1,8.31662986 11.1,7.88399347 C11.1,7.45103707 11.458677,7.1 11.9003267,7.1 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoMovie" viewBox="0 0 24 24">
                                <g>
                                    <path
                                        d="M11.9,1.9 C17.4227444,1.9 21.9,6.37736054 21.9,11.900225 C21.9,17.422712 17.4226719,21.9 11.9,21.9 C6.37732809,21.9 1.9,17.422712 1.9,11.900225 C1.9,6.37736054 6.37725559,1.9 11.9,1.9 Z M11.9,2.7 C6.81908759,2.7 2.7,6.81918415 2.7,11.900225 C2.7,16.9808825 6.81915429,21.1 11.9,21.1 C16.9808457,21.1 21.1,16.9808825 21.1,11.900225 C21.1,6.81918415 16.9809124,2.7 11.9,2.7 Z M9.03142857,7.78571429 C9.03142857,7.47248768 9.37514563,7.28079535 9.64163413,7.44540028 L9.64163413,7.44540028 L16.3028586,11.5599132 C16.5559252,11.7162277 16.5559161,12.0842497 16.3028418,12.2405516 L16.3028418,12.2405516 L9.64161732,16.3546101 C9.37512822,16.5191972 9.03142857,16.3275035 9.03142857,16.0142857 L9.03142857,16.0142857 Z M9.831,8.503 L9.831,15.296 L15.331,11.9 L9.831,8.503 Z">
                                    </path>
                                </g>
                            </symbol>
                            <symbol id="icoCoupon" viewBox="0 0 24 24">
                                <g>
                                    <path
                                        d="M19.7508,4.3 C20.6798328,4.3 21.4332,5.05320494 21.4332,5.9824 L21.4332,5.9824 L21.4332,10.6534789 L20.8396815,10.5628572 L20.7504,10.5576 C19.9920263,10.5576 19.3768,11.1734014 19.3768,11.9324 C19.3768,12.6913986 19.9920263,13.3072 20.7504,13.3072 L20.7504,13.3072 L20.7924061,13.3059657 L20.8975522,13.2946514 L21.4332,13.2113211 L21.4332,17.8824 C21.4332,18.8115951 20.6798328,19.5648 19.7508,19.5648 L19.7508,19.5648 L3.9824,19.5648 C3.05336723,19.5648 2.3,18.8115951 2.3,17.8824 L2.3,17.8824 L2.3,13.2113211 L2.76185558,13.2836116 L2.89343728,13.3019404 L2.9824,13.3072 C3.74112578,13.3072 4.3564,12.6914466 4.3564,11.9324 C4.3564,11.1733534 3.74112578,10.5576 2.9824,10.5576 L2.9824,10.5576 L2.89343728,10.5628596 L2.3,10.6534789 L2.3,5.9824 C2.3,5.05320494 3.05336723,4.3 3.9824,4.3 L3.9824,4.3 Z M19.7508,5.1 L3.9824,5.1 C3.49515645,5.1 3.1,5.49507132 3.1,5.9824 L3.1,5.9824 L3.099,9.762 L3.13766131,9.76306257 C4.21460549,9.83910855 5.07495326,10.7000925 5.15094161,11.7771293 L5.15094161,11.7771293 L5.1564,11.9324 C5.1564,13.133135 4.18309306,14.1072 2.9824,14.1072 L3.099,14.102 L3.1,17.8824 C3.1,18.294755 3.38292267,18.641056 3.76516067,18.7378502 L3.87173181,18.7579247 L3.9824,18.7648 L19.7508,18.7648 C20.2380435,18.7648 20.6332,18.3697287 20.6332,17.8824 L20.6332,17.8824 L20.633,14.102 L20.5951796,14.101737 C19.518512,14.0256854 18.65824,13.1646409 18.5822579,12.0876617 L18.5822579,12.0876617 L18.5768,11.9324 C18.5768,10.7317408 19.5500311,9.7576 20.7504,9.7576 L20.7504,9.7576 L20.633,9.762 L20.6332,5.9824 C20.6332,5.53255815 20.2964986,5.16132611 19.8614682,5.10687527 L19.8614682,5.10687527 L19.7508,5.1 Z M14.8432427,8.04657373 L15.4138773,8.60726627 L8.80427731,15.3340663 L8.23364269,14.7733737 L14.8432427,8.04657373 Z M14.20144,13.29048 C14.7537054,13.29048 15.20144,13.7382146 15.20144,14.2908368 C15.20144,14.8431022 14.7537054,15.2908368 14.20144,15.2908368 C13.6491746,15.2908368 13.20144,14.8431022 13.20144,14.2908368 C13.20144,13.7382146 13.6491746,13.29048 14.20144,13.29048 Z M9.38104,8.4702 C9.93330543,8.4702 10.38104,8.91793457 10.38104,9.4702 C10.38104,10.0228222 9.93330543,10.4705568 9.38104,10.4705568 C8.82877457,10.4705568 8.38104,10.0228222 8.38104,9.4702 C8.38104,8.91793457 8.82877457,8.4702 9.38104,8.4702 Z">
                                    </path>
                                </g>
                            </symbol>
                        </svg>
                    </div>
                </div>
                <div class="write_chat3">
                    <div class="wrap_inp">
                        <form action="#none">
                            <fieldset>
                                <legend class="screen_out">채팅 메시지 입력 폼</legend>
                                <div class="box_tf"><textarea id="chatWrite" class="tf_g" placeholder="메시지 보내기" style="overflow: auto;"></textarea></div>
                                <div class="write_menu">
                                    <div class="wrap_button">
                                        <div class="upload_btn "><input type="file" class="custom uploadInput" multiple="" style="width: 0px;"><button type="button" class="btn_menu" style="position: relative;"><span class="ico_chat ico_attatch"></span></button></div>
                                        <div class="layer_tooltip4" style="display: none;"><span class="txt_tooltip">파일 전송하기</span><span class="ico_chat ico_arr"></span></div>
                                    </div>
                                    <div class="wrap_button"><button class="btn_menu" type="button"><span class="ico_chat ico_answer"></span></button>
                                        <div class="layer_tooltip4"><span class="txt_tooltip">자주 쓰는 답변 선택</span><span class="ico_chat ico_arr"></span></div>
                                    </div>
                                    <div class="wrap_button"><button class="btn_menu" type="button"><span class="ico_chat ico_coupon"></span></button>
                                        <div class="layer_tooltip4"><span class="txt_tooltip">쿠폰 보내기</span><span class="ico_chat ico_arr"></span></div>
                                    </div>
                                    <div class="wrap_button"><button class="btn_menu" type="button"><span class="ico_chat ico_shop"></span></button>
                                        <div class="layer_tooltip4"><span class="txt_tooltip">쇼핑몰 상품정보</span><span class="ico_chat ico_arr"></span></div>
                                    </div>
                                </div><button class="btn_g btn_submit disabled" disabled="" type="button">전송</button>
                            </fieldset>
                        </form>
                    </div>
                </div><input type="file" multiple="" autocomplete="off" style="position: absolute; inset: 0px; opacity: 1e-05; pointer-events: none;">
            </div>
        </div>
    </div>
    <div></div>
</div>

'''
# Parse the HTML
root = html.fromstring(html_content)
# Flag to start recording chats
start_recording = False
# List to hold chat texts
chat_texts = []
# Find all p elements
# p_elements = root.xpath('//p')
# print('all:',p_elements)
p_elements = root.xpath('//p[@class="txt_check"] | //*[@class="item_chat item_start" or @class="item_chat"]//p')

# p_elements = root.xpath('//p')
print('less:', p_elements)
# Iterate through each p element
for p in p_elements:
    # print(p.attrib.get('class'))
    # If the p has the class 'txt_check', set the flag to start recording
    if 'txt_check' in p.attrib.get('class', ''):
        start_recording = True
    # If the flag is set and the p has the class 'txt_chat', record the chat
    if start_recording and 'txt_chat' in p.attrib.get('class'):
        chat_texts.append(p.text_content())
ret_texts = ""
# Print the chat texts
for chat_text in chat_texts:
    ret_texts += chat_text + '\n'

print(ret_texts)
# Print the chat texts
# for chat_text in chat_texts:
#     print(chat_text)
