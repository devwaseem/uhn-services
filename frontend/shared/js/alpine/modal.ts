export default () => ({
    show: false,
    open() {
        this.show = true;
        document.body.classList.add('overflow-hidden');
    },
    close() {
        this.show = false;
        document.body.classList.remove('overflow-hidden');
    },
});
