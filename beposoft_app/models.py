from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from .validators import validate_gst
import re
from django.core.exceptions import ValidationError
from decimal import Decimal
import random
from datetime import timedelta
from django.utils import timezone
from django.utils.timezone import now 
# Create your models here.


class State(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    class Meta :
        db_table = "State"

class Departments(models.Model):
    name = models.CharField(max_length=100)
    class Meta:
        db_table = "Departments"

    def __str__(self):
        return self.name

class Supervisor(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE)

    class Meta:
        db_table = "Supervisor"

    def __str__(self):
        return self.name


class Family(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta :
        db_table = "Family"



class User(models.Model):

    eid = models.CharField(max_length=6, unique=True, editable=False)
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100,unique=True,null=True)
    email = models.EmailField(max_length=100,unique=True)
    phone = models.CharField(max_length=100,unique=True)
    alternate_number = models.CharField(max_length=10, null=True, blank=True)
    password = models.CharField(max_length=100)
    image = models.ImageField(max_length=100, upload_to="staff_images/", null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    allocated_states = models.ManyToManyField(State, blank=True)
    gender = models.CharField(max_length=100, null=True, blank=True)
    marital_status = models.CharField(max_length=100, null=True, blank=True)
    driving_license = models.CharField(max_length=100, null=True, blank=True)
    driving_license_exp_date = models.DateField(null=True, blank=True)
    employment_status = models.CharField(max_length=100, null=True, blank=True) #(Full-time  Part-time Contract)
    designation = models.CharField(max_length=100, null=True, blank=True)
    grade = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    state = models.CharField(max_length=100, null=-True,blank=True)
    country = models.CharField(max_length=100,default='india', null=True, blank=True)
    join_date = models.DateField(null=True, blank=True)
    confirmation_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)
    supervisor_id = models.ForeignKey(Supervisor, on_delete=models.CASCADE, null=True)
    department_id = models.ForeignKey(Departments, on_delete=models.CASCADE, null=True)
    signatur_up = models.ImageField(upload_to="signature/",max_length=100,null=True)
    APPROVAL_CHOICES = [
        ('approved', 'Approved'),
        ('disapproved', 'Disapproved'),
    ]
    approval_status = models.CharField(max_length=100, choices=APPROVAL_CHOICES, default='disapproved', null=True)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Hash password if provided
        if 'password' in kwargs:
            self.password = make_password(kwargs['password'])
        elif not self.pk and self.password:  # Hash password for new user
            self.password = make_password(self.password)

        # Generate unique eid if not already set
        if not self.eid:
            self.eid = self.generate_unique_eid()

        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def generate_unique_eid(self):
        while True:
            eid = str(random.randint(100000, 999999))
            if not User.objects.filter(eid=eid).exists():
                return eid

    class Meta:
        db_table = "User"


class Attributes(models.Model):
    created_user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100) 

    def __str__(self):
        return self.name

    class Meta:
        db_table = "attributes"


class ProductAttribute(models.Model):
    attribute = models.ForeignKey(Attributes, on_delete=models.CASCADE)
    value = models.CharField(max_length=255) #ex RED BLACK L M 

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

    class Meta:
        db_table = "product_attributes" 


class Customers(models.Model):
    gst = models.CharField(
        unique=True,
        max_length=15,
        null=True,
        blank=True,
        validators=[validate_gst],  
    )
    name = models.CharField(max_length=100)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10,unique=True)
    alt_phone = models.CharField(max_length=10, null=True)
    email = models.EmailField(max_length=100,unique=True)
    address = models.CharField(max_length=500,null=True)
    zip_code =models.IntegerField()
    city = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500,null=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    
    class Meta :
        db_table = "Customers"
        
        
        
class Company(models.Model):
    name = models.CharField(max_length=100)
    gst = models.CharField(max_length=20)
    address = models.CharField(max_length=500, null=True)
    zip = models.IntegerField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=100)
    web_site = models.URLField()
    prefix = models.CharField(max_length=5, unique=True, help_text="Unique prefix for invoice numbers")

    def __str__(self):
        return self.name



class Shipping(models.Model):
    created_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=500)
    zipcode = models.IntegerField()
    city = models.CharField(max_length=100)
    state = models.ForeignKey(State,on_delete=models.CASCADE)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    class Meta :
        db_table = "Shipping_Address"

    def __str__(self):
        return self.name




class Products(models.Model):
    PRODUCT_TYPES = [
        ('single', 'Single'),
        ('variant', 'Variant'),
    ]
    
    UNIT_TYPES = [
        ('BOX', 'BOX'),
        ('NOS', 'NOS'),
        ('PRS', 'PRS'),
        ('SET', 'SET'),
        ('SET OF 12', 'SET OF 12'),
        ('SET OF 16', 'SET OF 16'),
        ('SET OF 6', 'SET OF 6'),
        ('SET OF 8', 'SET OF 8'),
    ]
    created_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=500)
    hsn_code = models.CharField(max_length=100)
    family = models.ManyToManyField(Family, related_name='familys')
    type = models.CharField(max_length=100, choices=PRODUCT_TYPES, default='single')
    unit = models.CharField(max_length=100, choices=UNIT_TYPES, default="BOX")
    purchase_rate = models.FloatField()
    tax = models.FloatField() 
    image = models.ImageField(upload_to='images/',null=True)
    exclude_price = models.FloatField(editable=False)  
    selling_price = models.FloatField(null=True)  
    stock = models.IntegerField(default=0)
    

    def calculate_exclude_price(self):
        if self.selling_price is not None:
            self.exclude_price = self.selling_price / (1 + self.tax / 100)
        else:
            self.exclude_price = 0

    def save(self, *args, **kwargs):
        self.calculate_exclude_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class SingleProducts(models.Model) :
    created_user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='single_products')
    image = models.ImageField(upload_to='images/')

    class Meta:
        db_table = "single_product"

    def __str__(self):
        return f"{self.product.name}"


class VariantProducts(models.Model):
    created_user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='variant_products')
    name = models.CharField(max_length=500)
    stock = models.PositiveBigIntegerField(default=0, null=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    is_variant = models.BooleanField(default=False)

    class Meta:
        db_table = "variant_product"

    def __str__(self):
        return self.name
    
    
class VariantImages(models.Model):
    variant_product = models.ForeignKey(VariantProducts, on_delete=models.CASCADE, related_name='variant_images')
    image = models.ImageField(upload_to='images/')
    class Meta:
        db_table = "variant_images"
        
    def __str__(self):
        return f"{self.variant_product.name} - {self.image}"
        
    


class ProductAttributeVariant(models.Model):
    variant_product = models.ForeignKey(VariantProducts, on_delete=models.CASCADE,related_name="sizes")
    attribute = models.CharField(max_length=100)
    stock = models.PositiveBigIntegerField(default=0)

    class Meta:
        db_table = "product_attribute_variant"

    def __str__(self):
        return f"{self.variant_product.name} - {self.attribute}"
    
class Bank(models.Model):
    created_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    open_balance = models.FloatField()
    class Meta:
        db_table = "Bank"
        
    def  __str__(self):
        return self.name





class Order(models.Model):
    manage_staff = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE,related_name="customer")
    invoice = models.CharField(max_length=20, unique=True, blank=True)
    billing_address = models.ForeignKey(Shipping, on_delete=models.CASCADE,related_name="billing_address")
    order_date = models.CharField(max_length=100)
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    code_charge = models.IntegerField(default=0,null=True)
    shipping_mode = models.CharField(max_length=100,null=True)
    shipping_charge = models.IntegerField(default=0,null=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('payed', 'payed'),
        ('COD', 'COD'),
        ('credit', 'credit'),
    ], default='payed')
    status = models.CharField(max_length=100, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Shipped', 'Shipped'),
        ('Invoice Created','Invoice Created'),
        ('Invoice Approved','Invoice Approved'),
        ('Waiting For Confirmation','Waiting For Confirmation'),
        ('To Print','To Print'),
        ('Invoice Rejectd','Invoice Rejectd'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Refunded', 'Refunded'),
        ('Return', 'Return'),
    ], default='Pending')
    total_amount = models.FloatField()
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE,related_name="bank")
    note = models.TextField(null=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('PayPal', 'PayPal'),
        ('Razorpay', 'Razorpay'),
        ('Net Banking', 'Net Banking'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cash on Delivery', 'Cash on Delivery'),
    ], default='Net Banking')
 
    time=models.TimeField(null=True)
    updated_at = models.DateField(auto_now_add=True,null=True, blank=True)
   

    def save(self, *args, **kwargs):
        if not self.invoice:
            self.invoice = self.generate_invoice_number()
            print(f"Generated invoice number: {self.invoice}")
        super().save(*args, **kwargs)

    def generate_invoice_number(self):
        if not self.company:
            raise ValueError("Company must be set to generate an invoice number.")
        
        prefix = self.company.prefix  # Retrieve prefix from the associated Company
        number = self.get_next_invoice_number(prefix)
        invoice_number = f"{prefix}{number}"
        return invoice_number

    def get_next_invoice_number(self, prefix):
        highest_invoice = Order.objects.filter(invoice__startswith=prefix).order_by('invoice').last()
        if highest_invoice:
            number = int(highest_invoice.invoice.split('-')[-1]) + 1
        else:
            number = 1
        return str(number).zfill(6)  # Zero-pad to 6 digits
    def update_status(self, new_status):
        """
        Updates the status and sets the updated_at field to the current time.
        """
        if self.status != new_status:  # Check if the status is changing
            self.status = new_status
            self.updated_at = now()  # Set current timestamp
            print(f"Status updated to '{new_status}' on {self.updated_at}")
            self.save()  # Save the changes
        else:
            print("No change in status.")

    def __str__(self):
        return f"Order {self.invoice} by {self.customer}"
    

    


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    variant = models.ForeignKey(VariantProducts, on_delete=models.CASCADE,null=True)
    size = models.ForeignKey(ProductAttributeVariant, on_delete=models.CASCADE,null=True)
    description = models.CharField(max_length=100,null=True)
    rate = models.IntegerField()  # without GST
    tax = models.PositiveIntegerField()  # tax percentage
    discount = models.IntegerField(default=0, null=True)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

    
        
        
        
class BeposoftCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    variant = models.ForeignKey(VariantProducts, on_delete=models.CASCADE,null=True,blank=True,)
    size = models.ForeignKey(ProductAttributeVariant,on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    discount = models.IntegerField(null=True, blank=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    class Meta:
        db_table = "beposoft_cart"
        
        
    
    
class PaymentReceipt(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment_receipts')
    customer = models.ForeignKey(Customers,on_delete=models.CASCADE,null=True)
    payment_receipt = models.CharField(max_length=10, unique=True, editable=False)  # Combined ID
    amount = models.CharField(max_length=100)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    transactionID = models.CharField(max_length=50)
    received_at = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    remark = models.TextField()

    def save(self, *args, **kwargs):
        # Generate a unique payment_receipt if not set
        if not self.payment_receipt:
            # Get the last receipt ID and increment
            last_id = PaymentReceipt.objects.all().order_by('id').last()
            next_id = last_id.id + 1 if last_id else 1
            # Create formatted ID, e.g., REC-0001A
            self.payment_receipt = f"REC-{str(next_id).zfill(4)}{chr(65 + (next_id % 26))}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Receipt #{self.payment_receipt} for Order: {self.order.invoice}"

    class Meta:
        db_table = "receipts"
        
    

class PerfomaInvoiceOrder(models.Model):
    COMPANY_CHOICES = [
        ('MICHEAL IMPORT EXPORT PVT LTD', 'MICHEAL IMPORT EXPORT PVT LTD'),
        ('BEPOSITIVERACING PVT LTD', 'BEPOSITIVERACING PVT  LTD'),
    ]

    manage_staff = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=100, choices=COMPANY_CHOICES, default='MICHEAL IMPORT EXPORT PVT LTD')
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE,related_name="perfoma_customer")
    invoice = models.CharField(max_length=20, unique=True, blank=True)
    billing_address = models.ForeignKey(Shipping, on_delete=models.CASCADE,related_name="perfoma_billing_address")
    order_date = models.CharField(max_length=100)
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    code_charge = models.IntegerField(default=0,null=True)
    shipping_mode = models.CharField(max_length=100,null=True)
    shipping_charge = models.IntegerField(default=0,null=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('payed', 'payed'),
        ('COD', 'COD'),
        ('credit', 'credit'),
    ], default='payed')
    status = models.CharField(max_length=100, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Shipped', 'Shipped'),
        ('Invoice Created','Invoice Created'),
        ('Invoice Approved','Invoice Approved'),
        ('Waiting For Confirmation','Waiting For Confirmation'),
        ('To Print','To Print'),
        ('Invoice Rejectd','Invoice Rejectd'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Refunded', 'Refunded'),
        ('Return', 'Return'),
    ], default='Pending')
    total_amount = models.FloatField()
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE,related_name="perfoma_bank")
    note = models.TextField(null=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('PayPal', 'PayPal'),
        ('Razorpay', 'Razorpay'),
        ('Net Banking', 'Net Banking'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cash on Delivery', 'Cash on Delivery'),
    ], default='Net Banking')


    def save(self, *args, **kwargs):
        if not self.invoice:
            self.invoice = self.generate_invoice_number()
            print(f"Generated invoice number: {self.invoice}")
        super().save(*args, **kwargs)

    def generate_invoice_number(self):
        prefix = ""
        if self.company == 'MICHEAL IMPORT EXPORT PVT LTD':
            prefix = "MI-"
        elif self.company == 'BEPOSITIVERACING PVT LTD':
            prefix = "BR-"
        
        number = self.get_next_invoice_number(prefix)
        invoice_number = f"{prefix}{number}"
        print(f"Invoice number generated: {invoice_number}")
        return invoice_number

    def get_next_invoice_number(self, prefix):
        # Get the highest existing invoice number for the given prefix
        highest_invoice = PerfomaInvoiceOrder.objects.filter(invoice__startswith=prefix).order_by('invoice').last()
        if highest_invoice:
            number = int(highest_invoice.invoice.split('-')[-1]) + 1
        else:
            number = 1
        return str(number).zfill(6)  # Zero-pad to 6 digits

    def __str__(self):
        return f"Order {self.invoice} by {self.customer}"
    


class PerfomaInvoiceOrderItem(models.Model):
    order = models.ForeignKey(PerfomaInvoiceOrder, on_delete=models.CASCADE, related_name='perfoma_items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    variant = models.ForeignKey(VariantProducts, on_delete=models.CASCADE,null=True)
    size = models.ForeignKey(ProductAttributeVariant, on_delete=models.CASCADE,null=True)
    description = models.CharField(max_length=100,null=True)
    rate = models.IntegerField()  # without GST
    tax = models.PositiveIntegerField()  # tax percentage
    discount = models.IntegerField(default=0, null=True)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
    

class Warehousedata(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='warehouse_orders')
    box=models.CharField(max_length=100)
    weight=models.CharField(max_length=30)
    length=models.CharField(max_length=30)
    breadth=models.CharField(max_length=30)
    height=models.CharField(max_length=30,null=True)
    image=models.ImageField(upload_to='images/',null=True)
    packed_by=models.ForeignKey(User,on_delete=models.CASCADE)
    parcel_service=models.CharField(max_length=30,null=True)  
    tracking_id=models.IntegerField(null=True)
    shipping_charge=models.DecimalField(max_digits=10, decimal_places=2,null=True)
    status=models.CharField(max_length=30,null=True)
    shipped_date=models.DateField()

    def __str__(self):
        return f"{self.box} - {self.parcel_service} ({self.tracking_id})"


class GRVModel(models.Model):
    STATUS_CHOICES=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    REMARK_CHOICES=[
        ('return','Return'),
        ('refund','Refund')
    ]
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    product=models.CharField(max_length=100)
    returnreason=models.CharField(max_length=200)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    quantity=models.IntegerField()
    remark=models.CharField(max_length=20,choices=REMARK_CHOICES,null=True)
    status=models.CharField(max_length=30,choices=STATUS_CHOICES,default='pending',null=True)
    date=models.DateField(null=True)
    time=models.TimeField(null=True)
    note=models.TextField(null=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def update_status(self, new_status):
        """
        Updates the status and sets the updated_at field to the current time.
        """
        if self.status != new_status:  # Check if the status is changing
            self.status = new_status
            self.updated_at = now()  # Set current timestamp
            print(f"Status updated to '{new_status}' on {self.updated_at}")
            self.save()  # Save the changes
        else:
            print("No change in status.")


class ExpenseModel(models.Model):
    company=models.ForeignKey(Company,on_delete=models.CASCADE)
    payed_by=models.ForeignKey(User,on_delete=models.CASCADE)
    bank=models.ForeignKey(Bank,on_delete=models.CASCADE)
    purpose_of_payment=models.TextField()
    amount=models.DecimalField(max_digits=10,decimal_places=2,null=True)
    expense_date=models.DateField()
    transaction_id=models.IntegerField()
    description=models.TextField()
    added_by=models.CharField(max_length=30,null=True)



    







   