############### 함수 설정 #########################################
import time
import datetime      ## 날짜
import pyupbit       ## 업비트
import pandas as pd  ## pandas
k=pd.Series()        ## pandas
import requests      ## 슬랙
############### 함수 설정 #########################################

############### 변수 선언문 #######################################
x = 30         ## 30분 간격 업데이트 선언
#Coins = 5      ## 코인수량
minimum = 10000 ## 최소금액
limit = 0.2    ## 손절가
ratio = 0.2    ## 비중
############### 변수 선언문 끝 ####################################

############### 시간 설정 ########################################
now = datetime.datetime.now()          ## 현재시간 21-11-21 09:41:33.039899
nowY = now.strftime('%Y-%m-%d %H:%M')  ## DateTitm 2021-11-21 09:41
nowD = now.strftime('%Y-%m-%d %H')     ## DATE 2021-11-21
nowm = now.strftime('%m')              ## Month 11
nowd = now.strftime('%d')              ## Day 21
nowHM = now.strftime('%H:%M')          ## Time 09:41
############### 시간 설정 끝 #####################################

############### 서버 접근 ########################################
access = "9k5gGxbmhqBuXXPlZsu9s57AJi3kTojPfh6wShQ5"
secret = "NyoLuuB2UxGnBo3WYXNtGL2Kzz9loOSmNtp456my"
myToken = "xoxb-2726106428551-2764476230592-2lKgOnt3VVPO4eDK08TJe24A"
############### 서버 접근 끝 #####################################

############### 슬랙 메시지 보내기 ################################
def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
############### 슬랙 메시지 보내기 끝 #############################

############### 업비트 로그인 ####################################
price = pyupbit.get_current_price
upbit = pyupbit.Upbit(access, secret)  ## 업비트 로그인
tickers=pyupbit.get_tickers(fiat="KRW") 
print("#########################################################")
print(str(now)+ ": 업비트 시작")  ##  업비트 시작
post_message(myToken,"#stock", str(now)+" : 업비트 시작") ## 시작 메세지 슬랙 전송
print("#########################################################")
#################################################################

############### 코인정보 가져오기 ################################
tickers=pyupbit.get_tickers(fiat="KRW")
############### 코인정보 가져오기 끝 #############################

############### 출력 테스트 #####################################
#print(nowY)
# print(nowd)
# print(nowm)
# print(nowD)
# print(nowHM)
############### 출력 테스트 끝 ###################################

# ret = upbit.buy_limit_order("KRW-XRP", 100, 20)  ## 리플 100원 20개 매수
# ret = upbit.sell_limit_order("KRW-XRP", 1000, 20) ## 리플 1000원 20개 매도

############### 자동 매매 기록 ###################################
## 작성날자 : 2021- 11-21
## 작성자 : 임동섭
## 작성내용 : 자동매매 시작
############### 자동 매매 시작 ###################################
while True:
    try:
        
        now = datetime.datetime.now() ## 날짜 
        nowm = now.strftime('%M')     ## 분 추출
        print(f"분 : " +str(nowm))    ## 인쇄
        
        if x-2 < int(nowm) :
            upbit.get_order("KRW-BTC")

            if x-1 < int(nowm) :   ##매시 x분 자산 업데이트
                ##업비트 현재가로 평가금 확인, 미체결 금액 확인
                quity = 0
                tailtotal = 0
                for ticker in tickers :
                    v=price(ticker)*upbit.get_balance(ticker)
                    quity += v
                    pending = upbit.get_order(ticker)
                    if len(pending) > 0 :
                        for o in range(0,len(pending)) :
                            tail = float(pending[o]['remaining_volume'])*float(pending[o]['price'])
                            tailtotal += tail
                업비트잔고 = upbit.get_balance("KRW") + quity + tailtotal

                # 메세지 보내기  
                nowf = now.strftime('%Y-%m-%d %H:%M') 
                T = nowf+"\n업비트 : "+str(int(업비트잔고))         
                post_message(myToken,"#stock",T) 
                print(T) 
                time.sleep(3300-(int(nowm)-x)*60) # x - 5분까지 대기
    
        print("###### 미체결 시작 ######")
        tickers=pyupbit.get_tickers(fiat="KRW")   ## 코인코드: KRW-BTC
        for ticker1 in tickers :                  ## 미체결 금액 총액 계산
            pending1 = upbit.get_order(ticker1)   ## pending1 코인코드 저장
            lp1=len(pending1)                     ## pending1 길이
            tailtotal = 0                         ## tailtotal 변수설정
            if lp1 > 0 :                          ## lp1 > 0 크면 실행(1개추출)
                tail = 0                          ## tails 변수설정
                tails = 0                         ## tails 변수설정
                for o in range(0,lp1) :           ## 0부터 lp1 까지 수행, (0,lp1,2): 2개간격
                    now = datetime.datetime.now() ## 날짜시간 설정
                    nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')  ## 날짜 시간 설정 
                    tail = int(float(pending1[o]['remaining_volume'])*float(pending1[o]['price'])+0.1)  ## 미체결금액
                    tails += tail                 ## 미체결금액 누적
                tailtotal += tails                ## 미체결금액 누적
                print(nowDatetime,ticker1,"미체결 수 :", str(len(pending1)),"미체결 금액 :", str(tails)) ## 미체결 수
            time.sleep(0.4)                       ##조회 1초 5회 제한
        ################ 미체결 끝 ###############
        
        print("###### 거래량 상위 시작 ######")
        for ticker2 in tickers: #거래량 상위 결정, 최근 16시간 거래금액
           df = pyupbit.get_ohlcv(ticker2,interval="minute240",count=4)  
           Coins = len(df)
           q=upbit.get_balance(ticker2)
           p = float(df['close'][3])
           v = float(df['value'][0]) + float(df['value'][1]) + float(df['value'][2]) + float(df['value'][3])

           if (1000< p <2500) or (100< p <500) or (10< p <50) or (1< p <5) or (0.1< p <0.5) or (p <0.05) : # 호가 단위 0.2% 이하
               v2=0
           else :
               v2=v
           k[ticker2]=float(v2) #float 타입으로 변환해준다
           l=k.sort_values(ascending=False) 
           vsup=l[0:Coins] # 호가단위 0.2 % 이하 인 종목 중 거래량 상위
        
        for ticker2 in tickers:                      ## 거래량 상위 결정, 최근 16시간 거래금액
            df2 = pyupbit.get_ohlcv(ticker2,interval="minute240",count=4)  ## 최근 4시간 정보 추출
            v = float(df2['value'][0]) + float(df2['value'][1]) + float(df2['value'][2]) + float(df2['value'][3])
            k[ticker2] = float(v)
            print(ticker2,v)
            time.sleep(0.2) # 1초당 5회 조회 제한 -> 'NoneType' object is not subscriptable
            
        l=k.sort_values(ascending=False) #거래량 상위 Desc
        #l=k.sort_values(by="Survived") # ASC
        vsup2=l[0:Coins] 
        vinf2=l[Coins:len(l)]
        ################ 거래량 상위 끝 ###############
        
        print("###### 비중 조절 시작 ######")
        for b in range(0,Coins) :
            ticker3=vsup2.index[b]
            p=pyupbit.get_current_price(ticker3)
            q=upbit.get_balance(ticker3)
            time.sleep(0.2) # 1초당 5회 조회 제한 -> 'NoneType' object is not subscriptable
            print(b, ticker3, "현재 종가",str(p), "현재 평가금",str(p*q) )
                 
            if p*q > minimum * (1-limit/100) / ratio : # 평가금 > 최소금액 * (손절가 / 최소 비중) 
                print(ticker3,"자산 전체 유지")

            else :                    
                if p*q> minimum * (1+limit/100):  # 평가금 > 최소금액 * 익절라인 -> 일부 익절
                    upbit.sell_limit_order(ticker3,p,q-minimum/p)
                    print(ticker3,"기본 금액 제외 매도") 
                    tickers=pyupbit.get_tickers(fiat="KRW")
                    for ticker3 in tickers:
                        pending3 = upbit.get_order(ticker3)
                        lp3=len(pending3)
                        print(ticker3,lp3)
                        if lp3 > 0 :
                            for o3 in range(0,lp3) :
                                if ( str(pending3[o3]['side']) == 'ask' ) and ( str(pending3[o3]['state']) == 'wait' ) :
                                    upbit.cancel_order(pending3[o3]['uuid'])
                                    ticP = pyupbit.get_tick_size(pyupbit.get_current_price(ticker3) * 0.90)
                                    upbit.sell_limit_order(ticker3, ticP, float(pending3[o3]['remaining_volume']))                                                    
                
                if p*q< minimum * (1-limit/100) : # 평가금 < 최소금액 * 손절라인 -> 추가 매수
                    upbit.buy_limit_order(ticker3,p,minimum/p-q)
                    print(ticker3,"기본 금액에 맞춰 추가 매수")
                #    orderbook = pyupbit.get_orderbook(ticker3) #호가 불러오기
                #     bids_asks = orderbook[0]['orderbook_units'] 
                #     ticP= float(bids_asks[0]['ask_price']) #윗호가
                #     ticN= float(bids_asks[0]['bid_price']) #아랫호가
                #     tic1N = pyupbit.get_tick_size(p * 0.995)
                #     tic2N = pyupbit.get_tick_size(p * 0.99)
                #     tic1P = pyupbit.get_tick_size(p * 1.005)
                #     tic2P = pyupbit.get_tick_size(p * 1.01)
                #     upbit.sell_limit_order(ticker3,p,0.4*(minimum/p-q))
                #     upbit.sell_limit_order(ticker3,ticP,0.1*(minimum/ticP-q))
                #     upbit.sell_limit_order(ticker3,ticN,0.1*(minimum/ticN-q))
                #     upbit.sell_limit_order(ticker3,tic1N,0.1*(minimum/tic1N-q))
                #     upbit.sell_limit_order(ticker3,tic2N,0.1*(minimum/tic2N-q))
                #     upbit.sell_limit_order(ticker3,tic1P,0.1*(minimum/tic1P-q))
                #     upbit.sell_limit_order(ticker3,tic2P,0.1*(minimum/tic2P-q))
                #     print(ticker3,"현재가, 윗호가, 아랫호가, +- 0.5, 1% 가격에 기본금액 분할 매수") 

            now = datetime.datetime.now()
            nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
            #bot.sendMessage(chat_id=chat_id, text=(nowDatetime+" 업비트 거래량 하위 항목 매도 시작")) 
            post_message(myToken,"#stock",nowDatetime+" 업비트 거래량 하위 항목 매도 시작") 

        for s in range(0,len(l)-Coins) :
            ticker4=vinf2.index[s]
            p= pyupbit.get_current_price(ticker4) # 종가
            q=upbit.get_balance(ticker4) # 수량
            print(s, ticker4, "현재 종가",str(p), "현재 평가금",str(p*q) )

            if q > 0 :
                if p*q> ((1-limit/100) / ratio) * minimum:
                    print(ticker4,"자산 유지")
                else :
                    if 1+limit/100<p*q/minimum<((1-limit/100)/ratio):
                        print(ticker4,"자산 일부 매도")
                        upbit.sell_limit_order(ticker4, p,(1+limit/100)*minimum/p)
                    else:
                        if p*q - limit/100 * minimum< 5000 :
                            print(ticker4,"자산 전체 매도")
                            upbit.sell_limit_order(ticker4,p,q)
                        else :
                            print(ticker4,"자산 최소 금액 * ",str(limit),"% 매도")
                            upbit.sell_limit_order(ticker4,p,limit*minimum/(100*p))
        ################ 비중 조절 끝 ###############  
    
    except Exception as err:    ## 예외 처리
        print(err)              ## 에러 출력
        #post_message(myToken,"#stock", str(now) +" "+ err +" "+ "에러가 발생했습니다.") ## 에러 발송
    time.sleep(10)              ## 10초 기다림 try 다시감
    
############### 자동 매매 끝 ####################################