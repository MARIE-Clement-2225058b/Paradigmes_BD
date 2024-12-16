rate = document.getElementById('rate');
console.log("submit");

document.querySelectorAll('.rating input').forEach(input => {
  input.addEventListener('change', (event) => {
    console.log("submit");
    rate.submit()
  });
});

