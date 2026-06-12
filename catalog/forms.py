"""
============================================================
FORMS — catalog/forms.py
============================================================
Defines custom forms used in the catalog app. Django forms
handle HTML form rendering, input validation, and data cleaning.

Currently contains one form:
  RenewBookModelForm — Used by librarians to set a new due date
                       for a borrowed book (renew_book_librarian view).
============================================================
"""

import datetime
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from catalog.models import BookInstance


class RenewBookModelForm(ModelForm):
    """
    BOOK RENEWAL FORM
    ============================================================
    A ModelForm based on the BookInstance model, exposing only
    the 'due_back' date field.

    Frontend display:
      - Rendered on catalog/book_renew_librarian.html
      - Shows a single date input with a label "New renewal date"
      - Help text explains the valid date range

    Validation rules (in clean_due_back):
      1. The new date must not be in the past
      2. The new date must not be more than 4 weeks in the future
    ============================================================
    """

    def clean_due_back(self):
        """
        Custom validation for the due_back field.

        Called automatically by Django when the form is submitted.
        If validation fails, the error message is displayed on the
        form page in the template (via {{ form.as_p }}).
        """
        data = self.cleaned_data['due_back']

        # VALIDATION 1: Date must not be in the past
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # VALIDATION 2: Date must not be more than 4 weeks ahead
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        return data

    class Meta:
        # Link this form to the BookInstance model
        model = BookInstance
        # Only expose the due_back field (not status, borrower, etc.)
        fields = ['due_back']
        # Custom label shown above the input on the form page
        labels = {'due_back': _('New renewal date')}
        # Help text shown below the input on the form page
        help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3).')}
