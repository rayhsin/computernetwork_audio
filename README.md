# computernetwork_audio
  前面的arg部份是前期（複製別人的code)也想說留給未來設定用的，
  其中samplerate是一秒取樣的次數，default是44100
  blocksize原本是想在livestreaming的時候傳送的單位，但是總之目前是不太可行了
  
  首先大guy說一下目前我技術上遇到的困難＆發現（我真的很認真的做qq
  因為是要做livestreaming
  同時還要implement flow control之類的功能
  我首先在我的電腦上可以作到錄音，並把錄音分塊，也可以幾塊幾塊存起來
  （e.g. 一塊1024bytes，一次存五塊）
  但是丟到html上就有點困難
  因為和video不一樣的地方是，video的code好像可以一張一張jpeg在傳的
  但是audio看起來不能。
  我後來看http的request訊息
  html的audio傳送有特定的規則（這是我直接上傳一個檔案收到的request）
    Host: localhost:5000
    Connection: keep-alive
    Accept-Encoding: identity;q=1, *;q=0
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36
    Chrome-Proxy: frfr
    Accept: */*
    Referer: http://localhost:5000/
    Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7
    Range: bytes=0-
  首先它要有request我才能傳送對吧
  如果是vedio的話我大可以傳送現在的jpeg給它
  但是audio它會要求Range，所以我必須讀他的request裡的header檔，然後我要切出他要的那個range給它
  （這是在前提是我可以控制flask的response所有內容，因為我在試著改他的內容的時候它不給我改qq）
  最讓我覺得不可能完成的地方是Range那一籃，只要滑鼠按在播放器上滑動
  它就會音滑鼠位置隨時監不同爆出成千上萬不同地方的range要求（像是Range: bytes=299764-這麼醜的），而正常的話flask的response就會回覆從那一個"byte"開始的片段給它
  但是livestreaming我自己手做不太可能完成阿，所以後來就放棄了
  （我覺得如果不是用html來做的話，也許就....限制比較少了？＝>但是時間成本太高）
  
  說到livestreaming
  坊間都是用flash實現的
  古時候html好像不能完成這件事情，
  而最近也有說html5可以透過mediasource實現
  但是後來實際實做之後才發現它只允許fmp4的檔案而已
  這樣會導致還需要把影像檔跟聲音轉成fmp4(不是mp4，qq)
  貌似不可能，所以我也放棄了
  
  最後我用最後的手段，一邊傳送影片一邊錄音
  美一段時間把錄音存起來，
  然後
