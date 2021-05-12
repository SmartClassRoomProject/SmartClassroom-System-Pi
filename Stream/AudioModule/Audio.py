from MySocket import UdpServer
import time


class RemoteAudio :
    def __init__(self,buffer_size = 4410):
        self.localIP = "192.168.0.177" 
        self.port = 8080
        self.buffer_intSize = buffer_size # 4 byte
        self.sock = UdpServer(self.buffer_intSize)
        self.sock.bind(self.localIP,self.port)
        
    def remote_read(self):
        res = []
        while len(res) < self.buffer_intSize:
            recv_ , size = self.sock.recv() # return 1 package from esp udp
            # print(size)
            res.extend(recv_[:size])   
            

        return res


if __name__ == "__main__" :
    pass
    
        # while True:  
        #     recv_ = sock.recv() # return 1 package from esp udp
        #     count_ += len(recv_)
        #     sample_1sec.extend(recv_)
        #     if count_ >= fs :
      
        #         for i in sample_1sec :
        #             print(i)

        #         count_ = 0
        #         sample_1sec = []

        #         count_sam += 1
        #         elapsed_time = time.time() - now
        #         sum_time += elapsed_time
        #         av_time = sum_time/count_sam
        #         print(elapsed_time)
        #         now = time.time()

              

                


                
                