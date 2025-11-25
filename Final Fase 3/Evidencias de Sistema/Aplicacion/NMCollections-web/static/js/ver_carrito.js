// Carrito page scripts extracted from template (relocated to root js)
(function(){
  function incrementarCantidad(btn) {
    const input = btn.parentElement.querySelector('input[name="cantidad"]');
    const max = parseInt(input.max) || 999;
    if (parseInt(input.value) < max) {
        input.value = parseInt(input.value) + 1;
        input.form.submit();
    }
  }
  function decrementarCantidad(btn) {
    const input = btn.parentElement.querySelector('input[name="cantidad"]');
    if (parseInt(input.value) > 1) {
        input.value = parseInt(input.value) - 1;
        input.form.submit();
    }
  }
  function actualizarBadgeCarrito() {
    if (!window.CARRITO_CANTIDAD_URL) return;
    fetch(window.CARRITO_CANTIDAD_URL)
      .then(r => r.json())
      .then(data => {
        const badge = document.querySelector('.cart-count');
        if (badge) badge.textContent = data.total_items;
      })
      .catch(()=>{});
  }
  document.addEventListener('DOMContentLoaded', actualizarBadgeCarrito);
  window.CarritoPage = { incrementarCantidad, decrementarCantidad };
})();
