function addMenuSvg() {
    const socials = document.getElementsByClassName("social-menu-item-link")

    for (let social of socials) {
        let request = new XMLHttpRequest()
        request.open('POST', '../static/images/svg/' + social.name + '.svg', false)
        request.send()
        social.innerHTML = `${request.responseText}`
        social.firstChild.setAttribute("class", "social-menu-item-svg")
    }
}