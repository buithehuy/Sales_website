# Sales_website
## Thành Viên
- Nguyễn Đức Anh - Bùi Thế Huy - Cao Tuấn Anh
- 22022661       - 22022667    -  22022562

### WEBSITE thương mại điện tự bán linh kiện máy tính.
- Link demo : https://www.youtube.com/watch?v=iUHA7fhtKcM
- Được xây dựng bằng <a href = 'https://www.djangoproject.com/'> Django </a> 
### Cách chạy dự án: ( Yêu cầu máy tính cài đặt docker )
- Xây dựng các image cần thiết.
  
      $ docker build -t web_sale .

- Khởi chạy container

       $ docker compose up
  
- Khởi tạo dữ liệu.
 
       $ docker exec sales_website-web-1 python manage.py migrate

- Truy cập trang web tại địa chỉ http://127.0.0.1:8000/
