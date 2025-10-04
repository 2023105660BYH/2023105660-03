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
                
                response=b"" 
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                filename = f"request_{timestamp}.bin"
                filepath = os.path.join(self.DIR_PATH, filename)


                with open(filepath, 'wb') as f:
                    while True:
                        try:
                            data = clnt_sock.recv(self.bufsize)
                            if not data:
                                break
                            response+=data
                            f.write(data)
                            if len(data) < self.bufsize:
                                break
                        except socket.timeout:
                            break
                
                header_end = response.find(b'\r\n\r\n')
                if header_end == -1:
                    return

                headers = response[:header_end].decode(errors='ignore')
                body = response[header_end + 4:]
                boundary = None
                for line in headers.split('\r\n'):
                    if line.lower().startswith('content-type: multipart/form-data'):
                        parts = line.split('boundary=')
                        if len(parts) == 2:
                            boundary = '--' + parts[1].strip()
                            break
                if not boundary:
                    return

                boundary_bytes = boundary.encode()
                parts = body.split(boundary_bytes)

                for part in parts:
                    if b'filename="' in part:
                        part_header_end = part.find(b'\r\n\r\n')
                        if part_header_end == -1:
                            continue
                        part_headers = part[:part_header_end].decode(errors='ignore')
                        file_content = part[part_header_end + 4:]
                        filename = 'uploaded_image'
                        for line in part_headers.split('\r\n'):
                            if 'filename="' in line:
                                start = line.find('filename="') + len('filename="')
                                end = line.find('"', start)
                                filename = line[start:end]
                                break
                        if file_content.endswith(b'\r\n'):
                            file_content = file_content[:-2]
                        if file_content.endswith(b'--'):
                            file_content = file_content[:-2]
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                        filename_only = os.path.basename(filename)
                        save_name = f"uploaded_{timestamp}_{filename_only}"
                        save_path = os.path.join(self.DIR_PATH, save_name)
                        with open(save_path, 'wb') as f:
                            f.write(file_content)  
                        break
                        
                # 응답전송
                print(response.decode(errors="replace"))
                clnt_sock.sendall(self.RESPONSE)
                
                # 클라이언트소켓닫기
                clnt_sock.close()
        except KeyboardInterrupt:
            print("\r\nStop the server...")
        # 서버소켓닫기
        self.sock.close()
if __name__=="__main__":
    server=SocketServer()
    server.run("127.0.0.1", 8000)
