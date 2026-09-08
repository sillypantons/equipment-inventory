# from urllib import request
# equipment list page, search, filter, sort and pagination functionality
# also calculated the next service date based on last service date and a 6 month interval (182 days) and displays it in the list view.

from datetime import timezone
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Equipment, EquipmentRequest
from django.db.models import Q
from django.core.paginator import Paginator

@login_required
def equipment_list(request):
    equipment = Equipment.objects.all()

    #search functionality
    query = request.GET.get("q", "")
    if query:
        equipment = equipment.filter(
            Q(SAGE_num__icontains=query) |
            Q(type__icontains=query) |
            Q(location__icontains=query) |
            Q(serial_number__icontains=query)
        )

    # filters -- location
    location_filter = request.GET.get("location", "")
    if location_filter:
        equipment = equipment.filter(location=location_filter)
    
    # Multi-checkbox filters for type -- getlist handles multiple values for the same key in the query params, e.g. ?type=Camera&type=Lens
    selected_types = request.GET.getlist("type")
    if selected_types:
        equipment = equipment.filter(type__in=selected_types)
    
    from django.db.models import F, ExpressionWrapper, DateField
    from django.utils import timezone
    from datetime import timedelta

    equipment = equipment.annotate(
        next_service_calc=ExpressionWrapper(
            F("last_service") + timedelta(days=182),
            output_field=DateField()
        )
    )

    # sorting functionality
    sort = request.GET.get("sort", "SAGE_num")  # default sort by SAGE_num  
    direction = request.GET.get("direction", "asc")  # default asc

    allowed_sorts = ["SAGE_num", "type", "location", "next_service_calc"]

    if sort in allowed_sorts:
        if direction == "desc":
            equipment = equipment.order_by(f"-{sort}")
        else:
            equipment = equipment.order_by(sort)
    else:
        equipment = equipment.order_by("SAGE_num")    # fallback default        

    # pagination
    paginator = Paginator(equipment, 20)  # 20 items per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)    # page_number if go back to old
    
    # Get distinct values for dropdowns
    # types = Equipment.objects.values_list('type', flat=True).distinct()
    locations = Equipment.objects.values_list('location', flat=True).distinct().order_by('location')

    return render(request, "inventory/equipment_list.html", {
        "page_obj": page_obj,
        "type_groups": get_type_groups(),  # get grouped types for checkboxes
        "locations": locations,
        'selected_types': selected_types, # passed back so checkboxes stay ticked
        "location_filter": location_filter,  # pass back so dropdown stays selected
        "query":           query,            # pass back so search box stays filled
    })

# how the filters are grouped in the equipment list page - 
# currently hard coded but could be made dynamic in future.

def get_type_groups():
    # Group equipment types by category based on keywords.
    all_types = Equipment.objects.values_list('type', flat=True).distinct().order_by('type')

    groups = {
        "Generators":    [],
        "Pumps":         [],
        "Submersibles":  [],
        "Dosing Pumps":  [],
        "Other":         [],
    }

    for t in all_types:
        t_lower = t.lower()
        if "generator" in t_lower:
            groups["Generators"].append(t)
        elif "beta" in t_lower or "sigma" in t_lower:
            groups["Dosing Pumps"].append(t)
        elif "sub" in t_lower:
            groups["Submersibles"].append(t)
        elif "pump" in t_lower:
            groups["Pumps"].append(t)
        else:
            groups["Other"].append(t)

    # Remove empty groups
    return {k: v for k, v in groups.items() if v}


from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from .forms import EquipmentRequestForm
from itertools import chain
# from operator import attrgetter
# creates request for equipment and logs it to the item history. Also displays the item history and request history on the item detail page.

def equipment_detail(request, SAGE_num):
    item = get_object_or_404(Equipment, SAGE_num=SAGE_num)
    request_history = EquipmentRequest.objects.filter(equipment=item)
    item_history    = EquipmentHistory.objects.filter(equipment=item)
    combined_history = sorted(
        chain(request_history, item_history),
        key=lambda x: x.date if hasattr(x, 'date') else x.date_requested,
        reverse=True
        )
    # service_form_value = get_service_form_value(item)

    if request.method == 'POST':
        form = EquipmentRequestForm(request.POST)
        if form.is_valid():
            name         = form.cleaned_data['requester_name']
            email        = form.cleaned_data['requester_email']
            request_type = form.cleaned_data['request_type']
            message_text = form.cleaned_data['message']

            EquipmentRequest.objects.create(
                equipment=item,
                requester_name=name,
                requester_email=email,
                request_type=request_type,
                message=message_text,
                status='pending',
            )

            # Log the request to item history
            # EquipmentHistory.objects.create(
            #     equipment=item,
            #     action='request',
            #     description=f"Request type: {request_type}\nMessage: {message_text}",
            #     performed_by=name,
            # )
            
            return render(request, 'inventory/request_successful.html', {'item': item})
    else:
        form = EquipmentRequestForm()

    return render(request, 'inventory/equipment_detail.html', {
        'item': item,
        'form': form,
        'combined_history': combined_history,
        # 'service_form_value': service_form_value(item),
    })

# might be worth perging all requests after a few years? or an option to delete certain ones after being completed.
# would deleting an item also delete that items request? 
# write offs?

def delete_request(request, request_id):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You need admin permission to access the request dashboard.")
        return redirect('equipment_list')

    eq_request = get_object_or_404(EquipmentRequest, id=request_id)

    # if request.method == 'POST':
    eq_request.delete()
    messages.success(request, "Request deleted successfully.")

    return redirect('request_dashboard')

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm

def is_admin(user):
    return user.is_staff  # only Django staff/admin users can access

# @login_required(login_url='login')
# @user_passes_test(is_admin, login_url='login')
# keep admin check if someone tries to access the dashboard throuf pasting url without admin account logged in.

def request_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You need admin permission to access the request dashboard.")
        return redirect('equipment_list')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    requests = EquipmentRequest.objects.all()

    if status_filter:
        requests = requests.filter(status=status_filter)

    return render(request, 'inventory/request_dashboard.html', {
        'requests': requests,
        'status_filter': status_filter,
    })


# @login_required(login_url='login')
# @user_passes_test(is_admin, login_url='login')
# in the dashboard will allow admins to change the status of requests to accepted, rejected, completed or left as pending.

def update_request_status(request, request_id, new_status):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You need admin permission to access the request dashboard.")
        return redirect('equipment_list')
    
    eq_request = get_object_or_404(EquipmentRequest, id=request_id)

    # if request.method == 'POST':
    #     new_status = request.POST.get('status')
    if new_status in ['pending', 'accepted', 'rejected', 'completed']:
        eq_request.status = new_status
        if new_status == 'completed':
            from django.utils import timezone
            eq_request.date_completed = timezone.now()
        else:
            eq_request.date_completed = None
        eq_request.save()

    return redirect('request_dashboard')


def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('request_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                return redirect('request_dashboard')
            else:
                form.add_error(None, "You do not have permission to access this page.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('login')


from django.forms import ModelForm
from django import forms

class EquipmentEditForm(ModelForm):
    class Meta:
        model = Equipment
        fields = ['type', 'serial_number', 'location', 'purchase_date', 'last_service', 'notes']
        widgets = {
            'type':          forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'location':      forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'last_service':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes':         forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


from .models import Equipment, EquipmentRequest, EquipmentHistory

# only admin roles can edit equipment details 
# Add a delete item function to remove equipment from the database if needed

def edit_equipment(request, SAGE_num):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You need admin permission to edit equipment.")
        return redirect('equipment_detail', SAGE_num=SAGE_num)

    item = get_object_or_404(Equipment, SAGE_num=SAGE_num)

    if request.method == 'POST':
        # Store old values before saving so we can log what changed
        old_values = {
            'type':          item.type,
            'serial_number': item.serial_number,
            'location':      item.location,
            'purchase_date': item.purchase_date,
            'last_service':  item.last_service,
            'notes':         item.notes,
        }

        form = EquipmentEditForm(request.POST, instance=item)
        if form.is_valid():
            form.save()

            # Build a description of what changed
            changes = []
            for field, old_val in old_values.items():
                new_val = getattr(item, field)
                if str(old_val) != str(new_val):
                    changes.append(f"{field.replace('_', ' ').title()}: '{old_val}' → '{new_val}'")

            description = "\n".join(changes) if changes else "No fields changed."

            from django.utils import timezone

            EquipmentHistory.objects.create(
                equipment=item,
                action='edited',
                description=description,
                performed_by=request.user.username,
                status='completed',             # status is completed as default as edits not checked (mainly for formatting)
                date_completed=timezone.now(),  # same as date made
            )

            messages.success(request, f"{SAGE_num} has been updated successfully.")
            return redirect('equipment_detail', SAGE_num=SAGE_num)
    else:
        form = EquipmentEditForm(instance=item)

    return render(request, 'inventory/edit_equipment.html', {
        'item': item,
        'form': form,
    })

from .forms import SignInOutForm
# signing in and out equipment items - to update location and tracking accuracy

def sign_in_out(request, SAGE_num):
    item = get_object_or_404(Equipment, SAGE_num=SAGE_num)

    if request.method == 'POST':
        form = SignInOutForm(request.POST)
        if form.is_valid():
            name         = form.cleaned_data['name']
            new_location = form.cleaned_data['new_location']
            old_location = item.location

            # Update the equipment location
            item.location = new_location
            item.save()

            from django.utils import timezone

            # Log to item history
            EquipmentHistory.objects.create(
                equipment=item,
                action='moved',
                description=f"Location changed from '{old_location}' to '{new_location}'",
                performed_by=name,
                status='completed',
                date_completed=timezone.now(),
            )

            messages.success(request, f"Location updated to {new_location} successfully.")
            return redirect('equipment_detail', SAGE_num=SAGE_num)
    else:
        form = SignInOutForm()

    return render(request, 'inventory/sign_in_out.html', {
        'item': item,
        'form': form,
    })

# in request dashboard allows for multiple rquests to be processed at once 
# current solution is a bit puggled might change in future.

def bulk_update_requests(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You need admin permission to access the request dashboard.")
        return redirect('equipment_list')

    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_requests')
        new_status   = request.POST.get('bulk_status')

        if not selected_ids:
            messages.error(request, "No requests selected.")
            return redirect('request_dashboard')

        if not new_status:
            messages.error(request, "No status selected.")
            return redirect('request_dashboard')

        requests_to_update = EquipmentRequest.objects.filter(id__in=selected_ids)

        for eq_request in requests_to_update:
            eq_request.status = new_status
            if new_status == 'completed':
                eq_request.date_completed = timezone.now()
            else:
                eq_request.date_completed = None
            eq_request.save()

        messages.success(request, f"{len(selected_ids)} request(s) updated to {new_status}.")

    return redirect('request_dashboard')

import pandas as pd
from datetime import datetime
from .forms import ExcelImportForm

# updates the data base with the excel file data - only for admin users

def import_equipment_view(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You need admin permission to access this page.")
        return redirect('equipment_list')

    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']

            # Check file extension
            if not excel_file.name.endswith(('.xlsx', '.xls')):
                messages.error(request, "Invalid file type. Please upload an Excel file.")
                return redirect('import_equipment_view')

            SHEETS = ["GEN", "PUMP", "SUBS", "DOSING"]
            total_created = 0
            total_updated = 0
            errors = []

            for sheet_name in SHEETS:
                try:
                    # Reset file pointer for each sheet read
                    excel_file.seek(0)
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    df.columns = df.columns.str.strip().str.lower()

                    created_count = 0
                    updated_count = 0

                    for _, row in df.iterrows():
                        raw_SAGE = row.get("sage reference")

                        if pd.isna(raw_SAGE):
                            continue

                        SAGE_num = str(raw_SAGE).strip().upper()

                        if not SAGE_num:
                            continue

                        equipment, created = Equipment.objects.update_or_create(
                            SAGE_num=SAGE_num,
                            defaults={
                                "type":          clean_string(row.get("equipment type")),
                                "serial_number": clean_string(row.get("serial number")),
                                "location":      clean_string(row.get("location")), 
                                # if moving to only setting a new location on creation, comment out the above line
                                "purchase_date": parse_date(row.get("date into service")),
                                "last_service":  parse_date(row.get("last service")),
                                "notes":         clean_string(row.get("notes")),
                            }
                        )

                        # Only set location if this is a brand new record
                        # if created:
                        #     equipment.location = clean_string(row.get("location"))
                        #     equipment.save()
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

                    total_created += created_count
                    total_updated += updated_count

                except Exception as e:
                    errors.append(f"Sheet '{sheet_name}': {str(e)}")

            if errors:
                for error in errors:
                    messages.warning(request, f"Warning — {error}")

            messages.success(request, f"Import complete: {total_created} created, {total_updated} updated across {len(SHEETS)} sheets.")
            return redirect('import_equipment_view')
    else:
        form = ExcelImportForm()

    # Get last import summary for display
    return render(request, 'inventory/import_equipment.html', {
        'form': form,
    })


# Helper functions used by the import view
def clean_string(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def parse_date(value):
    if pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None