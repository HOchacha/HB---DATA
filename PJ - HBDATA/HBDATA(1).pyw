import serial 
import pandas as pd
from tkinter import * 

import time
import threading 
import math

"""
HC - 06 연결
RXD - D12 연결
TXD - D11 연결

BT이름 : MECHA
"""
class User: 
    
    def __init__(self,name): 
        self.entityList = list()
        self.age = 20;
        self.HBMax = 220 - self.age
        self.HBavailable = 0 
        self.HBRest = 71 
        self.userName = str(name)
        self.HBavailable = self.HBMax - self.HBRest

    
        
    #추후 판다스를 사용하는 경우를 대비하여, 매직 메소드로 파일명을 반환한다. 
    def __str__(self):
        return str(self.userName) + '.xlsx'

    #구현 필요 부분, 해당되는 운동상태를 작성하면 될 것 같음 
    def BPM_Algorithsm(self, other):
        self.ProcessingIQR(other)
        
        self.BPMthresold = [self.getThresold(0), self.getThresold(1),self.getThresold(2)]
        try: 
            print(self.averageBPM)
            print(self.BPMthresold)
            if self.averageBPM < self.BPMthresold[0]:
                print("휴식상태")
                return 1
            elif self.averageBPM < self.BPMthresold[1]:
                print('지방연소구간')
                return 2
            elif self.averageBPM < self.BPMthresold[2]: 
                print("심장강화구간")
                return 3
            elif self.averageBPM > self.BPMthresold[2]:
                print('최대심박구간')
                return 4
        except: 
            print("입력값 오류")
        

    def ProcessingIQR(self,trial): 
        self.entityList.sort()

        self.Third_QuaterData = self.entityList[int(3/4*trial -1)] 
        self.A_QuaterData = self.entityList[int(1/4*trial-1)]

        self.IQR = abs(self.A_QuaterData - self.Third_QuaterData) 
        print(self.entityList)
        self.popTargetList = list()
        for i in range(len(self.entityList)): 
            print(i)
            if self.A_QuaterData - 1.5 * self.IQR < self.entityList[i] < self.Third_QuaterData + 1.5*self.IQR: 
                pass 
            else: 
                self.popTargetList.append(i)
        for i in self.popTargetList[::-1]: 
            self.entityList.pop(i)



        self.averageBPM = sum(self.entityList)/len(self.entityList)
        self.entityList.clear()

    def getThresold(self, index): 
        self.percentageHB = [0.4, 0.65, 0.8]
        print(self.HBMax, self.HBRest, self.HBavailable) 
        return (self.percentageHB[index]*self.HBavailable) + self.HBRest 


class mainApp(): 
    ##초기화면 구성
    def __init__(self): 
        self.userList = []
        self.nowUserIndex = 0 
        self.nowUserMax = 0
        self.arduino = 0

        self.window = Tk()
        self.semiWindow = 0

        self.NOWUSER = Label(self.window, text = "등록 필요", font=("Helvetica", 80))
        self.NOWUSER.pack()
        self.BPM = Label(self.window, text = "BPM : "+"NULL", font=("Helvetica", 80))
        self.BPM.pack() 
        self.STATUS = Label(self.window, text = "휴식상태", font = ("Helvetica", 80))
        self.STATUS.pack()


        self.CNUBTT = Button(self.window, text = "새로운 유저 추가", command = self.CreateNewUser1) 
        self.CNUBTT.pack() 
        self.SBCBTT = Button(self.window, text = "블루투스 연결 실행", command = self.SetSerialPortConnection)
        self.SBCBTT.pack()
        self.CNGUSERBTT = Button(self.window, text = "유저 변경", command= self.ChangeUser1)
        self.CNGUSERBTT.pack()
        

        self.STPLSDBTT = Button(self.window, text = "스레딩 정지", command = self.setIsWorking)
        self.STPLSDBTT.pack() 


        #블루투스 자동 연결, 시도 후 연결 실패시 오프라인 모드-데모 버전 
        ##아두이노 통신 파트, 스레딩 부분이므로 건들지 말 것
        self.setThreading = Button(self.window, text = "스레딩 시작", command = self.setThreadingFNC) 
        self.setThreading.pack() 

        self.window.mainloop() 

##################################################################################################################




    def setThreadingFNC(self):
        tread =threading.Thread(target = self.ListenSerialData )
        tread.start()

    def ListenSerialData(self): 
        self.isWorking = True 
        self.tempSerialData = 'null'
        self.trial = 0
        while self.isWorking:
            try: 
                self.arduino.write(b's')
                if self.arduino.readable(): 
                    print(self.arduino.readline().decode()[:len(self.arduino.readline().decode())-2])
                    #BPM 표시 부분
                    self.tempSerialData = self.arduino.readline().decode()[:len(self.arduino.readline().decode())-2]
                     
                    self.BPM.configure(text = "BPM : " + self.tempSerialData) 
            except serial.serialutil.SerialException: 
                print('오류가 발생했습니다.')
                self.setIsWorking()

            except AttributeError: 
                print("아두이노 연결을 먼저 하십시오")
                self.setIsWorking()
                break
            
            
            
            self.userList[self.nowUserIndex].entityList.append(int(self.tempSerialData))
            self.trial += 1
            print('시행 : ', self.trial)
            if self.trial == 12 :
               print("조건 충족 ")

               ###
               self.result = self.userList[self.nowUserIndex].BPM_Algorithsm(self.trial)
               self.trial = 0
               if self.result == 1: 
                   self.STATUS.configure(text = "심박수 구간 : 휴식상태")
               elif self.result == 2: 
                   self.STATUS.configure(text = "심박수 구간 : 지방 연소 구간")
               elif self.result == 3: 
                   self.STATUS.configure(text = '심박수 구간 : 심장 강화 구간')
               elif self.result == 4: 
                   self.STATUS.configure(text = "심박수 구간 : 최대 심박 구간")
                
        ###여기까지 건들지 말것 

###################################################################################
    
        
           

    #스레딩 반복 중지. 
    def setIsWorking(self): 
        if self.isWorking == True: 
            self.isWorking = False
        elif self.isWorking == False: 
            print('이미 스레딩이 정지되었습니다.')


    #30초간 심박수 안정을 가짐
    #2차 목표로 유예
    def ReadyforRestBPM(self): 
        pass 

        ###일시적으로 사용 중, 자동 연결 메소드로 준비할 것임. 
        ###아두이노가 지속적으로 연결되지 않는 경우, 오프라인 모드로 넘기는 메소드로 확장 필요
    def SetSerialPortConnection(self):
        try: 
            self.port ="COM8"
            self.baudrate = 115200
            self.arduino = serial.Serial(self.port, self.baudrate)
            print("성공적으로 " + str(self.port) +"에 연결 : ( baudrate : " + str(self.baudrate) + ")") 
        except serial.serialutil.SerialException: 
            print("이미 연결됨 혹은 아두이노가 연결되지 않음")
        except FileNotFoundError: 
            print("포트 설정이 잘못됨")
    
        ###뒤에 시리즈로 번호가 붙은 경우 절대로 건들지 말 것 

        ##유저 지칭 문제
        #이 쪽에서 유저의 나이까지 함께 입력할 수 있도록 수정할 수 있어?
        #추가적으로 휴식 심박수 값을 넣어줄 수 있게 할 수 있어?
    def CreateNewUser1(self) :
        self.writeName = Tk()
        Label(self.writeName, text = "사용자 이름 입력").grid(row = 0, column = 0)
        Label(self.writeName, text = "사용자 나이 입력").grid(row = 1, column = 0)
        self.nameInput = Entry(self.writeName)
        self.ageInput = Entry(self.writeName) 
        try: 
            while True: 
                #self.nameInput.bind("<Return>", self.CreateNewUser2) 
                self.nameInput.grid(row = 0, column = 1)
                self.ageInput.bind("<Return>", self.CreateNewUser2) 
                self.ageInput.grid(row = 1, column = 1)
                self.nameInput.mainloop() 
        except: 
            pass 
        
    #나이 입력 부분, 정수형 예외처리 부탁드립니다. 
    def CreateNewUser2(self, event):
         
        self.userList.append(User(str(self.nameInput.get())))
        self.userList[self.nowUserIndex].age = int(self.ageInput.get())
        self.userList.append(User(str(self.nameInput.get())))
        print(self.userList[self.nowUserIndex].age) 
        


        self.nowUserMax +=1
        print(self.nowUserIndex) 
        print(self.userList[self.nowUserIndex].userName)
        self.nowUserIndex = self.nowUserMax 
       
        self.writeName.quit()
        self.NOWUSER.configure(text = "USER : " + str(self.nameInput.get()))

    ##버그 수정 필요
    def ChangeUser1(self): 
        self.writeTargetUserNumber = Tk() 
        Label(self.writeTargetUserNumber, text = "변경할 사용자 번호 입력 : ").grid(row = 0 , column = 0)
        self.targetIndexInput = Entry(self.writeTargetUserNumber) 
        self.targetIndexInput.bind("<Return>", self.ChangeUser2)
        self.targetIndexInput.grid(row = 0, column = 1)

        self.writeTargetUserNumber.mainloop()

    def ChangeUser2(self, event): 
        #수정 완료
        try: 
            self.tempInput = int(self.targetIndexInput.get())
            self.nowUserIndex = self.tempInput 
            self.NOWUSER.configure(text = "USER : " + str(self.userList[self.nowUserIndex].userName))
            print("changeUser2 Successed")
        except: 
            print('올바른 유저 번호를 입력하세요')
        

k =mainApp()