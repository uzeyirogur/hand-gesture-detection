import cv2
import mediapipe as mp
import socket
import time

#Mediapipe için gerekli modüller 
mp_drawing = mp.solutions.drawing_utils #Görüntler üzerinde çizim yapmayı sağlayan modül. (Çizim için kullanılır)
mp_hands = mp.solutions.hands           #El tespitini ve elin içindeki önemli noktları tespit etmek için kullanılan modüldür.

# Video yakalama başlat
ekranGenislik = 640
ekranYukseklik = 480

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, ekranGenislik)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ekranYukseklik)


#Unity ile haberlesme islemi
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddressPort = ("127.0.0.1", 5052)

#El tespiti sınıfıkı kullanarak el tespiti işlemlerini başlatıyoruz.
"""
min_detection_confidence: Bu değer, elin tespit edilmesi için gerekli olan minimum güvenilirlik eşiğini belirtir. Yani, algılanan bir nesnenin gerçekten bir el olma olasılığı. Bu değer ne kadar yüksekse, algılanan elin gerçekten bir el olma olasılığı o kadar yüksek olur. Önerilen değerler arasında 0.5 ile 0.7 arası değerler bulunabilir.

min_tracking_confidence: Bu değer, elin izlenmesi için gerekli olan minimum güvenilirlik eşiğini belirtir. Yani, bir elin izlenmesi ve konumunun güncellenmesi için ne kadar güvenilir olması gerektiği. Bu değer de ne kadar yüksek olursa, algılanan elin takibi o kadar güvenilir olur. Önerilen değerler arasında 0.5 ile 0.7 arası değerler bulunabilir.
"""
with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.4) as hands:
    while cap.isOpened():
        # Video çerçevesini oku
        #ret = kare okuma degeri basarili ise True olur
        #frame = okunan karenin kendisidir. 
        ret, frame = cap.read()
        frame = cv2.flip(frame,1)

        # Çerçeveyi BGR'den RGB'ye dönüştür
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # RGB görüntüyü işle ve elleri tespit et
        results = hands.process(rgb_frame)

        # El tespiti başarılıysa
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                
                #elNoktaKoordinatları = dict.fromkeys(["WRIST,THUMB_CMC", "THUMB_MCP", "THUMB_IP,THUMB_TIP", "INDEX_FINGER_MCP", "INDEX_FINGER_PIP", "INDEX_FINGER_DIP","INDEX_FINGER_TIP", "MIDDLE_FINGER_MCP", "MIDDLE_FINGER_PIP",  "MIDDLE_FINGER_DIP", "MIDDLE_FINGER_TIP", "RING_FINGER_MCP", "RING_FINGER_PIP", "RING_FINGER_DIP", "RING_FINGER_TIP", "PINKY_MCP","PINKY_PIP", "PINKY_DIP", "PINKY_TIP"] )

                """elNoktaKoordinatları = dict()
                for i in range(21):
                    isaret_x, isaret_y, isaret_z = int(hand_landmarks.landmark[i].x * ekranGenislik), int(hand_landmarks.landmark[i].y * ekranYukseklik), int(hand_landmarks.landmark[i].z * ekranYukseklik)
                    elNoktaKoordinatları[i] = [isaret_x,isaret_y,isaret_z]"""

                #hand_idx degiskeni tespit edilen elin indis numarasını verir
                #hand_landmakrs tespit edilen el noktalarının hepsinin kordinatlarını tutan bir objedir...
                # Her elin 21 önemli noktasını çerçeve üzerine çiz

                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                #print(f" Bas parmak noktaları\n\n  4.Nokta:{int(hand_landmarks.landmark[8] * ekranYukseklik)}\n  " )

                elKoordinatlariStr = ""

                for i in range(21):
                    isaret_x, isaret_y, isaret_z = int(hand_landmarks.landmark[i].x * ekranGenislik), int(hand_landmarks.landmark[i].y * ekranYukseklik), int(hand_landmarks.landmark[i].z * ekranYukseklik)
                    elKoordinatlariStr += str([i,isaret_x,isaret_y,isaret_z]) + "."


                #Degerleri gonderme islemi yapıyoruz.
                sock.sendto(str.encode(elKoordinatlariStr), serverAddressPort)

                print(f" dongu : {elKoordinatlariStr.rstrip('.')} \n\n")




# Görüntüyü göster
        cv2.imshow('El Yakalama', frame)

        # Çıkış için 'q' tuşuna bas
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Video yakalamayı ve pencereyi kapat
cap.release()
cv2.destroyAllWindows()