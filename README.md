Nama: Muhammad Fairus Azfar Arisandi

NPM: 2506588752

Kelas: PBP F

### Tugas 1
1. Ya, saya menggunakan elemen semantik HTML5, seperti <section> untuk membagi page menjadi beberapa bagian. Saya juga menggunakan <artile> pada bagian education untuk mengelompokkan setiap riwayat pendidikan. Selain itu, dengan adanya elemen semantik, mempermudah proses styling menggunakan css dan membuat kode menjadi lebih terorganisir dan mudah dibaca.
2. Tantangan yang saya temukan ketika membuat css menjadi responsif ialah mengatur konten yang berpotensi menjadi overflow ketika tampilan mobile. Pada tampilan desktop, elemen bisa diatur lebih lebar karena memiliki ruang yang cukup. Namun, pada tampilan mobile, perlu dilakukan penyesuaian supaya elemen menjadi tidak overflow. Contoh yang saya alami ialah ketika menyusun riwayat pendidikan. Pada tampilan desktop, memungkinkan untuk menampilkannya secara horizontal, tetapi di mobile harus dibuat secara vertikal.
3. Karena web ini masih berupa static, informasi yang ditampilkan harus diubah secara langsung melalui kode HTML. Selain itu, ketika membuat carrousel pada section skills, saya harus menaruh logo berulang kali. Berdasarkan permasalahan tersebut, saya ingin menambahakan penggunaan backend dan database untuk mempermudah melakukan manipulasi pada web.

### Tugas 2
1. Ketika user mengakses URL portofolio, request tersebut diterima oleh urls.py pada proyek. Kemudian, file ini  mencocokkan dan meneruskan ke file urls.py pada aplikasi main. Selanjutnya, file ini menerukan ke views.py. File views.py bertindak sebagai controller yang memproses request tersebut dan mengakses database berdasarkan kebutuhan models. Setelah itu, models.py mengirimkan kembali data ke views.py untuk diteruskan ke template dan menampilkan ke user.
2. Menyimpan data pada model digunakan untuk memisahkan data dan tampilan. Jika data ditulis secara hardcode, setiap perubahan harus dilakukan melalui file HTML yang rentan mengubah struktur tampilan. Dengan menggunakan model, data disimpan di database. Jika ingin melakukan perubahan data, user bisa melakukannya melalui halaman admin tanpa perlu mengubah struktur HTML-nya. Dengan begitu, aplikasi menjadi lebih scalable untuk penambahan fitur yang akan datang.
3. Fungsi makemigrations digunakan sebagai pendeteksi dan pencatat perubahan yang ada pada models.py, lalu membuat file migrations yang berisi perubahan pada models.py. Sedangkan, perintah migrate berfungsi sebagai eksekutor yang membaca file migrations untuk melakukan perubahan pada database. Contohnya ialah ketika ingin menambahkan models Education. Setelah membuat struktur data pada models.py, perlu melakukan perintah makemigrations untuk membuat file migrations yang berisi penambahan data pada models.py. Setelah itu, baru menjalankan perintah migrate untuk mengimplementasikan penambahan tersebut pada database.

### AI Disclosure
Tools yang digunakan: Gemini
Selama mendevelop website ini, saya menggunakan AI untuk mempelajari best practice dalam proses membangun sebuah website meskipun belum sepenuhnya saya implementasikan. Sejauh ini, saya tidak (belum) menggunakan AI Coding Assistant untuk membantu proses saya membangun website portofolio ini. Bagi saya, mempelajari fundamental seperti ini merupakan fondasi krusial bagi perkembangan saya ke depannya.