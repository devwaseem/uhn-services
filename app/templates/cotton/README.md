# Django Cotton Components

This directory contains Cotton components for form inputs. These components
mirror the existing form templates under `app/templates/components/` but are
**not** wired into any pages yet.

Example usage:

```
<c-form-input field="{{ form.email }}" input_class="" />

<c-form-textarea field="{{ form.bio }}" rows="4" input_class="" />

<c-form-select field="{{ form.role }}" input_class="" />

<c-form-errors form="{{ form }}" />
```
