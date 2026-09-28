Nama: Muhammad Fairus Azfar Arisandi

NPM: 2506588752

Kelas: PBP F

## 🚀 Panduan Instalasi & Setup Lokal

Ikuti langkah-langkah berikut untuk menjalankan proyek ini di komputer lokal Anda:

### 1. Clone Repository
```bash
git clone https://github.com/fairusarisandi/myportofolio.git
cd myportofolio
```

### 2. Buat dan Aktifkan Virtual Environment
**Windows:**
```bash
python -m venv env
env\Scripts\activate
```
**macOS / Linux:**
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Instalasi Dependensi
Pastikan `pip` sudah diperbarui, lalu instal paket yang dibutuhkan:
```bash
pip install -r requirements.txt
```

### 4. Migrasi Database
Terapkan skema model ke dalam database lokal:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Konfigurasi Akun Admin & Group Editor
Untuk dapat mengakses fitur tambah, ubah, dan hapus data, buat akun *superuser* terlebih dahulu:
```bash
python manage.py createsuperuser
```
*(Opsional)* Untuk menguji hak akses grup **Editor**:
1. Jalankan server dan buka `http://localhost:8000/admin/`.
2. Masuk menggunakan akun *superuser* yang baru dibuat.
3. Buka menu **Groups** -> **Add Group**, lalu buat grup dengan nama **`Editor`**.
4. Masukkan pengguna pilihan Anda ke dalam grup **`Editor`** melalui menu **Users**.

### 6. Jalankan Server
```bash
python manage.py runserver
```
Buka *browser* dan akses aplikasi di `http://localhost:8000/`.

### Tugas 1
1. Ya, saya menggunakan elemen semantik HTML5, seperti <section> untuk membagi page menjadi beberapa bagian. Saya juga menggunakan <artile> pada bagian education untuk mengelompokkan setiap riwayat pendidikan. Selain itu, dengan adanya elemen semantik, mempermudah proses styling menggunakan css dan membuat kode menjadi lebih terorganisir dan mudah dibaca.
2. Tantangan yang saya temukan ketika membuat css menjadi responsif ialah mengatur konten yang berpotensi menjadi overflow ketika tampilan mobile. Pada tampilan desktop, elemen bisa diatur lebih lebar karena memiliki ruang yang cukup. Namun, pada tampilan mobile, perlu dilakukan penyesuaian supaya elemen menjadi tidak overflow. Contoh yang saya alami ialah ketika menyusun riwayat pendidikan. Pada tampilan desktop, memungkinkan untuk menampilkannya secara horizontal, tetapi di mobile harus dibuat secara vertikal.
3. Karena web ini masih berupa static, informasi yang ditampilkan harus diubah secara langsung melalui kode HTML. Selain itu, ketika membuat carrousel pada section skills, saya harus menaruh logo berulang kali. Berdasarkan permasalahan tersebut, saya ingin menambahakan penggunaan backend dan database untuk mempermudah melakukan manipulasi pada web.

### Tugas 2
1. Ketika user mengakses URL portofolio, request tersebut diterima oleh urls.py pada proyek. Kemudian, file ini  mencocokkan dan meneruskan ke file urls.py pada aplikasi main. Selanjutnya, file ini menerukan ke views.py. File views.py bertindak sebagai controller yang memproses request tersebut dan mengakses database berdasarkan kebutuhan models. Setelah itu, models.py mengirimkan kembali data ke views.py untuk diteruskan ke template dan menampilkan ke user.
2. Menyimpan data pada model digunakan untuk memisahkan data dan tampilan. Jika data ditulis secara hardcode, setiap perubahan harus dilakukan melalui file HTML yang rentan mengubah struktur tampilan. Dengan menggunakan model, data disimpan di database. Jika ingin melakukan perubahan data, user bisa melakukannya melalui halaman admin tanpa perlu mengubah struktur HTML-nya. Dengan begitu, aplikasi menjadi lebih scalable untuk penambahan fitur yang akan datang.
3. Fungsi makemigrations digunakan sebagai pendeteksi dan pencatat perubahan yang ada pada models.py, lalu membuat file migrations yang berisi perubahan pada models.py. Sedangkan, perintah migrate berfungsi sebagai eksekutor yang membaca file migrations untuk melakukan perubahan pada database. Contohnya ialah ketika ingin menambahkan models Education. Setelah membuat struktur data pada models.py, perlu melakukan perintah makemigrations untuk membuat file migrations yang berisi penambahan data pada models.py. Setelah itu, baru menjalankan perintah migrate untuk mengimplementasikan penambahan tersebut pada database.

### Tugas 3
1. Dengan menggunakan ModelForm, kita daat melakukan pembuatan field HTML secara otomatis berdaasarkan struktur model database. Hal tersebut dapat mengurangi penulisan kode HTML yang berulang serta mempermudah penyimpanan dengan menggunkaan form.save() untuk menambahkan data ke database. Selanjutnya, penggunaan {% csrf_token %} digunakan untuk mencegah adanya request dari web lain. Token ini memastikan bahwa pengiriman dataa berasal dari web user yang sedang digunakan.
2. JSON lebih disukai karena formatnya yang lebih rapi, ringkas, dan ringan dibanding XML. Kemudian, ukuran JSON yang lebih kecil juga membuat transfer data menjadi lebih cepat.
3. User mengirim request ke URL website, lalu fungsi view akan mencocokkaan URL. Selanjutnya, fungsi view mengambil data portofolio dari database menggunakan QuerySet. Kemudian, data QuerySet diproses menggunakan serialization menjadi JSON dan mengembalikannya di dalam HttpResponse. Proses serialization dilakukan untuk mengubah objek python dari database menjadi JSON. Hal tersebut dilakukan karena protokol HTTP hanya bisa mentransfer data berbasis teks dan browser tidak bisa membaca objek python.

### AI Disclosure
Tools yang digunakan: Gemini
Selama mendevelop website ini, saya menggunakan AI untuk mempelajari best practice dalam proses membangun sebuah website meskipun belum sepenuhnya saya implementasikan. Sejauh ini, saya tidak (belum) menggunakan AI Coding Assistant untuk membantu proses saya membangun website portofolio ini. Bagi saya, mempelajari fundamental seperti ini merupakan fondasi krusial bagi perkembangan saya ke depannya.