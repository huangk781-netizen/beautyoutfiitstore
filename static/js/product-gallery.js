(function () {
  const mainImage = document.getElementById('product-main-image');
  const mainVideo = document.getElementById('product-main-video');
  const thumbnails = Array.from(document.querySelectorAll('.gallery-thumbnail'));

  if (thumbnails.length < 2) return;

  thumbnails.forEach((thumbnail) => {
    thumbnail.addEventListener('click', () => {
      const isVideo = thumbnail.dataset.mediaType === 'video';

      if (isVideo && mainVideo) {
        if (mainImage) mainImage.classList.add('hidden');
        mainVideo.src = thumbnail.dataset.mediaSrc;
        if (thumbnail.dataset.mediaPoster) {
          mainVideo.poster = thumbnail.dataset.mediaPoster;
        } else {
          mainVideo.removeAttribute('poster');
        }
        mainVideo.classList.remove('hidden');
        mainVideo.load();
      } else if (!isVideo && mainImage) {
        if (mainVideo) {
          mainVideo.pause();
          mainVideo.classList.add('hidden');
        }
        mainImage.src = thumbnail.dataset.mediaSrc;
        mainImage.classList.remove('hidden');
      }

      thumbnails.forEach((item) => {
        const selected = item === thumbnail;
        item.setAttribute('aria-pressed', String(selected));
        item.classList.toggle('border-accent', selected);
        item.classList.toggle('border-transparent', !selected);
      });
    });
  });
})();
