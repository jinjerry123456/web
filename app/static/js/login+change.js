// the slide box
let flag = true
const mySwitch = () => {
    if (flag) {
        // get the slide box dom element and change its transform style
        $(".pre-box").css("transform", "translateX(100%)")
        // change the background color
        $(".pre-box").css("background-color", "#c9e0ed")
        // change the image
        // $("img").attr("src", "./img/wuwu.jpeg")

    }
    else {
        $(".pre-box").css("transform", "translateX(0%)")
        $(".pre-box").css("background-color", "#edd4dc")
        // $("img").attr("src", "./img/waoku.jpg")
    }
    flag = !flag
}

const bubleCreate = () => {
    // get the log-box element
    const body = document.getElementsByClassName('log-box')[0]
    // create a span element
    const buble = document.createElement('span')
    // add the class name
    let r = Math.random() * 5 + 25
    // set the style
    buble.style.width = r + 'px'
    buble.style.height = r + 'px'
    // create the animation
    buble.style.left = Math.random() * innerWidth + 'px'
    body.append(buble)
    setTimeout(() => {
        buble.remove()
    }, 4000)
}
// every 200ms create a buble
setInterval(() => {
    bubleCreate()
}, 200);
