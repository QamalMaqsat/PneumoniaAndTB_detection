document.getElementById('imageUpload').onchange = function (e) {
    const reader = new FileReader();
    reader.onload = function(){
        const uploadedImage = document.getElementById('uploadedImage');
        uploadedImage.src = reader.result;

        // Получение названия файла
        const fileName = e.target.files[0].name;

        // Отображение только первых 10 символов названия файла и его расширения
        const shortFileName = fileName.length > 10 ? fileName.substring(0, 10) + '...' : fileName;

        // Изменение текста кнопки "Обзор"
        document.getElementById('uploadButton').textContent = shortFileName;

        // Переместить кнопку обзор под изображение
        document.querySelector('.upload-container').appendChild(document.querySelector('.result-button-container'));
    }
    reader.readAsDataURL(e.target.files[0]);
}
