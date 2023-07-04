# Đối với người chơi bằng cách nhập tay

* B1: Khởi tạo đối tượng game (xem 2 cell đầu tiên ở file a.ipynb). Chạy phương thức "game.start_new_game()" để bắt đầu trò chơi.

* B2: Người chơi xem các thông tin và chọn ra các mã chứng khoán, tỉ lệ tiền đầu tư ứng với mỗi mã. Các thông tin có thể xem được như sau:
    - interest_rate: Lãi suất khi gửi ngân hàng.
    - account_balance: Số tiền hiện có để đem đầu tư.
    - data: Dữ liệu của chu kì đầu tư hiện tại và các dữ liệu quá khứ trước chu kì đầu tư hiện tại.
    - investment_history: Lịch sử đầu tư mà người chơi đã nhập vào.
    - profit_history: Lịch sử lợi nhuận, là kết quả của các lần đầu tư mà người chơi đã nhập.

    Để xem các thông tin trên, gõ "game.<thông tin muốn truy cập>" và ấn chạy.

* B3: Sau khi đã có các mã chứng khoán và tỉ lệ đầu tư ứng với mỗi mã, người chơi sẽ thực hiện đầu tư bằng cách chạy phương thức "game.invest(inv_obj, cycle)" với "cycle" là chu kì đầu tư. "inv_obj" có thể là một dictionary hoặc là một ndarray, list. Quy định về "inv_obj" phần sau.

# Đối với người code agent đầu tư

* Agent mẫu: xem file Ann.py hoặc Mai.py trong thư mục "Agents/".

* Hàm "get_investment_object" là hàm bắt buộc phải có. Hàm này có thể trả ra dictionary, ndarray hoặc list.

* Các thuộc tính có thể truy cập tại Agent:
    - interest_rate
    - account_balance
    - data
    - investment_history
    - profit_history

    Lưu ý: các thuộc tính public khác của class Game là vô nghĩa với Agent. Người code có thể định nghĩa các thuộc tính và các phương thức khác ở lớp Agent để hỗ trợ cho hàm đưa ra quyết định đầu tư (hàm get_investment_object).

* Chạy code và xem kết quả:
    - B1: Khởi tạo đối tượng game (xem 2 cell đầu tiên ở file a.ipynb).
    - B2: Chạy phương thức "game.run_agent_code". Phương thức này sẽ tải và chạy tất cả agent có mặt ở folder "Agents/".
    - B3: Xem kết quả:
        + Lịch sử đầu tư: agent_investment_history
        + Lịch sử lợi nhuận: agent_profit_history
        + Số tiền sau cùng: agent_account_balance
        Các thuộc tính trên đều ở dạng list. Ví dụ để xem lịch sử lợi nhuận của agent đầu tiên trong folder "Agents/" thì chạy đoạn code "game.agent_profit_history[0]".

# Quy định về "inv_obj"

* investment_object, là đầu vào của hàm "invest" và đầu ra của phương thức "get_investment_method".

* Nếu là dạng dictionary, các keys sẽ là các mã Chứng khoán, các values sẽ là tỉ lệ tiền đầu tư vào mã CK tương ứng.

Lưu ý 1: Nếu có mã CK không có trong chu kì đầu tư hiện tại thì mã CK đó sẽ bị tự động loại bỏ.

Lưu ý 2: Nếu tổng các values ở các mã CK đúng mà lớn hơn 1 thì sẽ tự động chia các values cho tổng các values (để đưa tổng các values về 1).

Lưu ý 3: Không được xuất hiện value âm.

* Nếu là dạng list hoặc ndarray, thì nó phải có độ dài bằng số mã CK có thể đầu tư. Các giá trị lần lượt tương ứng với các mã CK theo thứ tự trong data.