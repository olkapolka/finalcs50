// set current year in footer

var year = document.querySelector('.year');
var nowYear = new Date().getFullYear();
year.innerHTML = nowYear;

// change date format
var dates = document.querySelectorAll('.news-date');
dates.forEach(element => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    newDate = new Date(element.innerHTML);
    formattedDate = newDate.toLocaleDateString(undefined, options);
    element.innerHTML = formattedDate;
});
