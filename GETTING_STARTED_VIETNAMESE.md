# Chào mừng, luật sư — AI Brain của bạn bắt đầu từ đây

Bạn không cần phải là lập trình viên. Bạn cần một laptop (Mac hoặc Windows), kết nối internet để cài đặt, và 30 phút. Nếu bạn có thể sao chép-dán, bạn có thể sử dụng công cụ này.

> **English:** [GETTING_STARTED.md](GETTING_STARTED.md)

---

## Đây là gì, trong một đoạn văn

Một công cụ miễn phí biến laptop của bạn thành trợ lý văn phòng luật riêng tư nhỏ. Nó ghi nhớ các vụ việc của bạn (mọi hồ sơ vụ án, mọi bên, mọi lệnh, mọi ngày xét xử). Nó xác thực trích dẫn Bluebook. Nó cho bạn biết tòa án liên bang nào có thẩm quyền. Nó gắn cờ các rủi ro theo Quy tắc Mẫu ABA số 7 và các vấn đề tuân thủ CCPA. Nó chạy **trên chính máy tính của bạn** — không đám mây, không tải lên, không bên thứ ba nào đọc dữ liệu khách hàng của bạn. Giấy phép MIT. Bạn sở hữu mọi thứ bạn đưa vào đó.

## Tại sao luật sư hành nghề độc lập tại Hoa Kỳ nên quan tâm

Các hãng luật lớn có đội ngũ luật sư để kiểm tra trích dẫn, quản lý vụ việc và soạn thảo. Bạn chỉ có chính mình và một chiếc laptop. Đây là bộ não thứ hai của bạn.

- **Bạn quên ít hơn.** Bối cảnh vụ việc từ nhiều tháng trước trở lại ngay lập tức.
- **Bạn bỏ lỡ ít thời hạn hơn.** Ngày xét xử, thời hạn nộp đơn và thời hiệu khởi kiện được theo dõi.
- **Bạn duy trì tuân thủ ABA.** Tường lửa tích hợp gắn cờ rủi ro quảng cáo (Quy tắc 7), vấn đề hành nghề đa thẩm quyền (MR 5.5) và bảo mật (MR 1.6).
- **Bạn tiết kiệm tiền.** Westlaw/PACER/LexisNexis tốn hàng nghìn đô mỗi năm. Công cụ này là $0.
- **Dữ liệu của bạn vẫn riêng tư.** Các vụ việc của khách hàng KHÔNG BAO GIỜ rời khỏi laptop của bạn.

## Có gì bên trong

7 chuyên gia sống trong terminal của bạn:

1. **Nhân viên tiếp tân (bộ não)** — tìm hiểu bạn cần gì và điều hướng đến đúng chuyên gia.
2. **Thư ký trích dẫn** — xác thực trích dẫn Bluebook (SCOTUS, F.3d, F.Supp.3d, U.S.C., C.F.R.).
3. **Thư ký tòa án** — biết các tòa án liên bang: SCOTUS, 13 circuit, 94 district, bankruptcy, tax.
4. **Người quản lý vụ việc** — quản lý hồ sơ vụ án đang hoạt động (các bên, phiên xét xử, lệnh, thời hạn).
5. **Trợ lý soạn thảo** — kết nối với plugin soạn thảo wolfgang_rush (v0.2+).
6. **Nhân viên tuân thủ** — ABA MR 7, 5.5, 1.6, Ý kiến Chính thức 512 (đạo đức AI), CCPA/CPRA, FinCEN CTA.
7. **Trình theo dõi thời hạn** — thời hiệu khởi kiện, thời hạn nộp đơn, ngày xét xử (FRCP Quy tắc 6).

## Cài đặt nhanh

```bash
pip install git+https://github.com/Wolfgangrush/ai-law-firm-usa.git
ailawfirm_usa
```

## Dùng thử

```bash
ailawfirm_usa court "scotus"
ailawfirm_usa cite "347 U.S. 483 (1954)"
ailawfirm_usa cite "42 U.S.C. § 1983"
```

## Phạm vi

v0.1 **tập trung vào Liên bang.** Bao gồm SCOTUS, tòa án liên bang circuit/district, FRCP/FRCrP/FRE, Quy tắc Mẫu ABA và trích dẫn Bluebook. Các mô-đun cụ thể theo tiểu bang (CA CRC, NY CPLR, quy tắc đoàn luật sư tiểu bang) sẽ có trong v0.2+. Tất cả 50 tiểu bang được liệt kê dưới dạng placeholder.

## Quyền riêng tư

Mọi thứ chạy cục bộ. Các vụ việc khách hàng, hồ sơ vụ án và dữ liệu lịch của bạn vẫn ở trên laptop của bạn. Không tải lên đám mây. Không truy cập của bên thứ ba. Không đo lường từ xa.
