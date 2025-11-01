# CGRA Mapping

### Tóm tắt:

Kiến trúc Coarse-Grain Reconfigurable Arrays (CGRAs) đang nổi lên như một giải pháp tiết kiệm năng lượng nhằm tăng tốc các vòng lặp tính toán chuyên sâu trong ứng dụng. Tuy nhiên, mức độ tăng tốc mà một CGRA có thể mang lại phụ thuộc rất lớn vào chất lượng ánh xạ, tức là khả năng biên dịch hiệu quả vòng lặp lên nền tảng phần cứng này. Các kỹ thuật biên dịch tiên tiến hiện nay thường sử dụng modulo scheduling – một chiến lược nhằm tối thiểu hóa khoảng lặp II (Iteration Interval) cần thiết để thực thi vòng lặp, thông qua các thuật toán đồ thị phổ biến như liệt kê Max-Clique.

Trong nghiên cứu này, chúng tôi tiếp cận bài toán ánh xạ dưới dạng mô hình SAT, cho phép khám phá không gian lời giải hiệu quả hơn so với các công cụ hiện tại. Để xây dựng bài toán SAT, chúng tôi đề xuất một lịch trình riêng có tên là Kernel Mobility Schedule (KMS), được sử dụng kết hợp với đồ thị dữ liệu (DFG) và thông tin kiến trúc CGRA để tạo thành một tập các biểu thức logic mô tả đầy đủ các ràng buộc cần thỏa mãn khi ánh xạ với một II cụ thể. Sau đó, SAT solver sẽ được sử dụng để điều hướng không gian lời giải phức tạp này. Giống như các phương pháp hiện tại, quy trình là lặp lại: nếu không tồn tại ánh xạ hợp lệ cho II hiện tại, giá trị II sẽ được tăng lên và một KMS cùng tập ràng buộc mới sẽ được sinh ra và giải tiếp.

Kết quả thực nghiệm cho thấy SAT-MapIt đạt kết quả tốt hơn so với các phương pháp hiện tại trong 47,72% các benchmark được thử nghiệm: trong đó có trường hợp tìm được II thấp hơn, và cả những trường hợp tìm được ánh xạ hợp lệ mà các phương pháp trước không thể tìm ra.

## Yêu cầu hệ thống
Dự án này được phát triển và kiểm thử trên hệ điều hành Ubuntu 20.04.6.
Để tạo các tệp cấu hình CMake, chúng tôi sử dụng CMake phiên bản 3.23, và để biên dịch dự án, chúng tôi sử dụng ninja phiên bản 1.10.0.

## Khởi tạo:
1. Chạy file `setup.sh` để biên dịch LLVM và cấu hình môi trường Python.
2) Trước khi sử dụng trình biên dịch, hãy kích hoạt môi trường ảo bằng lệnh:
``` bash
source cgra-compiler/bin/activate
```

## Mã nguồn hỗ trợ
Trong thư mục `benchmarks` bạn sẽ tìm thấy các đoạn mã mẫu có thể được ánh xạ lên kiến trúc CGRA.
Để biên dịch mã của riêng bạn, chỉ cần thêm dòng  ```#pragma cgra acc``` trước vòng lặp mà bạn muốn ánh xạ lên CGRA.

**Lưu ý**: Hiện tại, trình biên dịch chỉ hỗ trợ:
- Các vòng lặp nằm sâu nhất
- Các vòng lặp không chứa lời gọi hàm hoặc câu lệnh điều kiện.

## Hướng dẫn biên dịch
Sau khi thêm chỉ thị ```#pragma cgra acc```  cho mã của bạn, biên dịch nó bằng lệnh sau:

```bash
./cgralang -f benchmarks/sha2/sha.c
```

Theo mặc định, mã sẽ được biên dịch cho kiến trúc CGRA kích thước 4x4.
Để chỉ định kích thước CGRA khác, sử dụng tuỳ chọn `-x` and `-y`.

## Output
Kết quả đầu ra của trình biên dịch là một tệp có tên `cgra-code-acc`, chứa nhiều thông tin debug và kết quả ánh xạ.

## Kết quả ví dụ trực quan:
1) ASAP, ALAP, MS:

<img width="204" height="297" alt="image" src="https://github.com/user-attachments/assets/c14c9132-f805-4e30-b044-d7d30a6490b2" /><img width="164" height="307" alt="image" src="https://github.com/user-attachments/assets/97c1d566-d8ca-4784-8443-8c1404b58529" />
<img width="397" height="311" alt="image" src="https://github.com/user-attachments/assets/e971d035-b9ed-4d8b-99e7-37c61c745bcb" />

2) Kết quả chạy tìm II thỏa mãn:
<img width="1232" height="364" alt="image" src="https://github.com/user-attachments/assets/b057c5de-710c-4ef6-b15b-e97ae4290fc2" />
<img width="209" height="315" alt="image" src="https://github.com/user-attachments/assets/8a636418-74f2-4491-a303-5aea3187ce45" />
<img width="146" height="234" alt="image" src="https://github.com/user-attachments/assets/d33a6bb9-0d2a-4b73-8c56-929bcae104be" />

3) Ứng dụng phần cứng:
<img width="408" height="443" alt="image" src="https://github.com/user-attachments/assets/e2e5783e-f553-4bd8-abdf-88c05fb5cc41" />
<img width="387" height="407" alt="image" src="https://github.com/user-attachments/assets/c5497832-16ae-4493-82df-6abab72bd7b7" />
<img width="620" height="458" alt="image" src="https://github.com/user-attachments/assets/ea898e28-34e7-439e-9975-a0413bce5881" />







