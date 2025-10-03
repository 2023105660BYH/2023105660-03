import os
import socket
from datetime import datetime 
class SocketServer:
    def __init__(self):
        self.bufsize=1024 # 버퍼크기설정
        with open('./response.bin', 'rb') as file:
            self.RESPONSE=file.read()  # 응답파일읽기
            
        self.DIR_PATH='./request'
        self.createDir(self.DIR_PATH)

    def createDir(self, path):
        """디렉토리생성"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("Error: Failed to create the directory.")
    
    def run(self, ip, port):
        """서버실행"""
        # 소켓생성
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(10)
        print("Start the socket server...")
        print("\"Ctrl+C\"for stopping the server!\r\n")
        
        try:
            while True:
                # 클라이언트의요청대기
                clnt_sock, req_addr=self.sock.accept()
                clnt_sock.settimeout(5.0)  # 타임아웃설정(5초)
                print("Request message...\r\n")
                
                response=b"" # 여기에구현하세요 
                
                # 응답전송
                clnt_sock.sendall(self.RESPONSE)
                
                # 클라이언트소켓닫기
                clnt_sock.close()
        except KeyboardInterrupt:
            print("\r\nStopthe server...")
        # 서버소켓닫기
        self.sock.close()
        if __name__=="__main__":
            server=SocketServer()
            server.run("127.0.0.1", 8000)