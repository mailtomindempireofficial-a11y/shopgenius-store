document.addEventListener('DOMContentLoaded',function(){
    document.querySelectorAll('.flash').forEach(function(el){
        setTimeout(function(){el.style.opacity='0';el.style.transform='translateY(-10px)';setTimeout(function(){el.remove()},300)},4000);
    });
});
