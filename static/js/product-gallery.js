(function () {
  const mainImage = document.getElementById('product-main-image');
  const thumbnails = Array.from(document.querySelectorAll('.gallery-thumbnail'));

  if (!mainImage || thumbnails.length < 2) return;

  thumbnails.forEach((thumbnail) => {
    thumbnail.addEventListener('click', () => {
      mainImage.src = thumbnail.dataset.galleryImage;
      thumbnails.forEach((item) => {
        const selected = item === thumbnail;
        item.setAttribute('aria-pressed', String(selected));
        item.classList.toggle('border-accent', selected);
        item.classList.toggle('border-transparent', !selected);
      });
    });
  });
})();
