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
<img width="223" height="311" alt="image" src="https://github.com/user-attachments/assets/75716ffa-58fb-4fa5-878c-12e9a5a1757d" />

Theo mặc định, mã sẽ được biên dịch cho kiến trúc CGRA kích thước 4x4.
Để chỉ định kích thước CGRA khác, sử dụng tuỳ chọn `-x` and `-y`.

## Output
Kết quả đầu ra của trình biên dịch là một tệp có tên `cgra-code-acc`, chứa nhiều thông tin debug và kết quả ánh xạ.
