import Alpine from 'alpinejs';
import 'https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js';
import { toast } from 'vanilla-sonner';
import 'vanilla-sonner/style.css';

import dropdown from '@shared/js/alpine/dropdown';
import modal from '@shared/js/alpine/modal';

function toastErrors() {
    const errorValues = document.scripts.namedItem('toast-errors');
    if (errorValues) {
        const errors = JSON.parse(errorValues.textContent);
        if (errors) {
            for (const error of errors) {
                toast.error(error);
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    toastErrors();
    document.querySelectorAll('[x-cloak]').forEach((el) => {
        el.removeAttribute('x-cloak');
    });
});

// @ts-ignore
function toastError() {
    toast.error('Something went wrong');
}

// @ts-ignore
window.sendEvent = (name: string) => {
    const event = new CustomEvent(name);
    window.dispatchEvent(event);
};

declare global {
    interface Window {
        Alpine: typeof Alpine;
    }
}

window.Alpine = Alpine;

Alpine.data('dropdown', dropdown);
Alpine.data('modal', modal);

Alpine.start();
