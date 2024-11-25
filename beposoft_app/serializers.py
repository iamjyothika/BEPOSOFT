from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from datetime import datetime
from django.db.models import Sum





class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    retype_password = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(required=True)  # Assuming phone is a required field

    class Meta:
        model = User
        fields = ['name', 'email', 'username', 'password', 'retype_password', 'phone']

    def validate(self, data):
        if data['password'] != data['retype_password']:
            raise serializers.ValidationError("Passwords do not match")
        
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("A user with this email already exists")
        
        if User.objects.filter(phone=data['phone']).exists():
            raise serializers.ValidationError("A user with this phone number already exists")
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('retype_password')

        user = User.objects.create(**validated_data)
        
        return user


    

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = "__all__"
        
        
    def validate(self, data):
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("A user with this email already exists")
        
        if User.objects.filter(phone=data['phone']).exists():
            raise serializers.ValidationError("A user with this phone number already exists")
        
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("A user with this username already exists")
        
        # if User.objects.filter(alternate_number = data['alternate_number']).exists():
        #     raise serializers.ValidationError("A user with this alternate number already exists")
        
        return data



class UserUpdateSerilizers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class StaffSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='department_id.name', read_only=True)

    class Meta:
        model = User
        fields = ['id','eid','name','department','join_date','phone','email','designation','family']


class CustomerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = [
            'id', 'gst', 'name', 'manager', 'phone', 'alt_phone', 'email',
            'address', 'zip_code', 'city', 'state', 'comment', 'created_at'
        ]
        
        
        
class CustomerModelSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Customers
        fields = [
            'id', 'gst', 'name', 'manager', 'phone', 'alt_phone', 'email',
            'address', 'zip_code', 'city', 'state', 'comment', 'created_at'
        ]

    def validate(self, data):
        if Customers.objects.filter(gst=data.get('gst')).exists():
            raise serializers.ValidationError({'gst': 'GST number is already registered.'})
        
        if Customers.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError({'email': 'Email is already registered.'})
        
        if Customers.objects.filter(phone=data.get('phone')).exists():
            raise serializers.ValidationError({'phone': 'Phone number is already registered.'})

        return data

    # If you want to handle uniqueness checks during updates, override update() method
    def update(self, instance, validated_data):
        gst = validated_data.get('gst', instance.gst)
        email = validated_data.get('email', instance.email)
        phone = validated_data.get('phone', instance.phone)

        # Start a transaction to ensure atomicity
        with transaction.atomic():
            # Check if GST is already registered excluding current instance
            if Customers.objects.filter(gst=gst).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError({'gst': 'GST number is already registered.'})

            # Check if email is already registered excluding current instance
            if Customers.objects.filter(email=email).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError({'email': 'Email is already registered.'})

            # Check if phone is already registered excluding current instance
            if Customers.objects.filter(phone=phone).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError({'phone': 'Phone number is already registered.'})

            # Perform the update operation
            return super().update(instance, validated_data)


class CustomerModelSerializerView(serializers.ModelSerializer):
    state = serializers.CharField(source='state.name', read_only=True)
    manager = serializers.CharField(source ='manager.name',read_only=True)
    class Meta:
        model = Customers
        fields = [
            'id', 'gst', 'name', 'manager', 'phone', 'alt_phone', 'email',
            'address', 'zip_code', 'city', 'state', 'comment', 'created_at'
        ]      
class ProductsSerializer(serializers.ModelSerializer):
    family = serializers.PrimaryKeyRelatedField(many=True, queryset=Family.objects.all())

    class Meta:
        model = Products
        fields = ['id', 'name', 'hsn_code', 'family', 'type', 'unit', 'purchase_rate', 'tax', 'selling_price', 'stock', 'image']



class CustomerSerilizers(serializers.ModelSerializer):
    class Meta :
        model = Customers
        fields = "__all__"



class SingleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleProducts
        fields = "__all__"
        
class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = "__all__"
        
        
class SizeSerializers(serializers.ModelSerializer):
    class Meta :
        model = ProductAttributeVariant
        fields = ["id","attribute","stock"]
        
class VariantImageSerilizers(serializers.ModelSerializer):
    class Meta :
        model = VariantImages
        fields  = ["id","image"]
        
class VariantProductSerializerView(serializers.ModelSerializer):
    created_user = serializers.CharField(source="created_user.name") 
    variant_images = VariantImageSerilizers(many=True, read_only=True) 
    sizes = SizeSerializers(many=True, read_only=True)

    class Meta:
        model = VariantProducts
        fields = ['id', 'created_user', 'name', 'stock', 'color', 'is_variant', 'variant_images',"sizes"]
        
    def to_representation(self, instance):
        # Call the parent method to get the default representation
        representation = super().to_representation(instance)

        # If 'is_variant' is False, remove 'sizes' from the serialized output
        if instance.is_variant:
            representation.pop('stock', None)  # Hide stock if is_variant is True
        else:
            representation.pop('sizes', None)  # Hide sizes if is_variant is False
        return representation

class ProductSerializerView(serializers.ModelSerializer):
    single_products = SingleProductSerializer(many=True, read_only=True)
    variant_products = VariantProductSerializerView(many=True, read_only=True)
    

    class Meta:
        model = Products
        fields = [
            "id", "created_user", "name", "hsn_code", "type", "unit", 'family',
            "purchase_rate", "tax", "image", "exclude_price", "selling_price", "stock","single_products","variant_products"
        ]
        
    def to_representation(self, instance):
        # Call the parent method to get the default representation
        representation = super().to_representation(instance)

        # If the product type is 'single', only show 'single_products' and 'stock'
        if instance.type == 'single':
            representation.pop('variant_products', None)  # Hide variant_products
        # If the product type is 'variant', only show 'variant_products'
        elif instance.type == 'variant':
            representation.pop('single_products', None)  # Hide single_products
            representation.pop('stock', None)  # Hide stock if type is variant
        
        return representation

    
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = "__all__"


class DepartmentSerilizers(serializers.ModelSerializer):
    class Meta :
        model = Departments
        fields = "__all__"


    



class StateSerializers(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = "__all__"



class SupervisorSerializerView(serializers.ModelSerializer):
    department = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Supervisor
        fields = ["id","name","department"]
        
class SupervisorSerializers(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = "__all__"

class SupervisorViewSerializers(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    class Meta:
        model = Supervisor
        fields = ['id', 'name', 'department', 'department_name']


class ShippingSerializers(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = "__all__"

    def create(self, validated_data):
        created_user = self.context['created_user']
        
        validated_data['created_user'] = created_user
        return Shipping.objects.create(**validated_data)
    
    
    
class ShippingAddressView(serializers.ModelSerializer):
    state = serializers.CharField(source='state.name', read_only=True)
    class Meta:
        model = Shipping
        fields = ["id","name","email","zipcode","address","phone","country","city","state"]



class VariantProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantProducts
        fields = "__all__"
        

class VariantImageSerilizers(serializers.ModelSerializer):
    class Meta :
        model = VariantImages
        fields  = ["id","image"]
        

class SizeSerializers(serializers.ModelSerializer):
    class Meta :
        model = ProductAttributeVariant
        fields = "__all__"
        

# class VariantProductSerializerView(serializers.ModelSerializer):
#     created_user = serializers.CharField(source="created_user.name") 
#     variant_images = VariantImageSerilizers(many=True, read_only=True) 
#     sizes = SizeSerializers(many=True, read_only=True)

#     class Meta:
#         model = VariantProducts
#         fields = ['id', 'created_user', 'name', 'stock', 'color', 'is_variant', 'variant_images',"sizes"]

class SingleProductsViewSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="product.name")
    class Meta:
        model = SingleProducts 
        fields = ['id','product','image','name']

    

class SingleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleProducts
        fields = "__all__"
        
        
class ExistedOrderAddProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"
    


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'name', 'description', 'rate', 'tax', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    customer=CustomerModelSerializer
    billing_address=ShippingSerializers
    class Meta:
        model = Order
        fields = "__all__"

class OrderInvoiceSerializer(serializers.ModelSerializer):
    # Define the fields you want to include in the response
    manage_staff_name = serializers.CharField(source='manage_staff.name', read_only=True)
    family_name = serializers.CharField(source='family.name', read_only=True)
    company_name=serializers.CharField(source='company.name',read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'invoice', 'order_date', 'status', 'shipping_mode', 'manage_staff_name',  
            'family_name','company_name'  
         
            
        ]        



















        
class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = "__all__"
        

class PaymentRecieptsViewSerializers(serializers.ModelSerializer):
    created_by = serializers.CharField(source="created_by.name")
    bank = serializers.CharField(source="bank.name")

    
    class Meta :
        model = PaymentReceipt
        fields = '__all__'


class PaymentReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentReceipt
        fields = ['amount']       


class OrderPaymentSerializer(serializers.ModelSerializer):
    payment_receipts = PaymentReceiptSerializer(many=True)
    
    # We will calculate the total paid amount by summing the amount from all related payment receipts
    total_paid = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'invoice', 'order_date', 'payment_status', 'status', 'payment_receipts', 'manage_staff', 'customer', 'total_paid']

    def get_total_paid(self, obj):
        # Calculate the total paid amount from all related payment receipts for this order
        total_paid = obj.payment_receipts.aggregate(total_paid=Sum('amount'))['total_paid'] or 0
        return total_paid

          








class WarehousedataSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source="order.customer.name")
    invoice = serializers.CharField(source = "order.invoice")
    family=serializers.CharField(source="order.family.name") 


    class Meta:
        model = Warehousedata
        fields = [
            'id', 'box', 'weight', 'length', 'breadth', 'height', 'image',
            'parcel_service', 'tracking_id', 'shipping_charge', 'status',
            'shipped_date','order', 'packed_by','customer','invoice','family'
        ]
class WarehouseBoxesDataSerializer(serializers.ModelSerializer):
    class Meta:
        model=Warehousedata
        fields='__all__'

              

  
    def get_volume_weight(self, obj):
        try:
            # Ensure length, breadth, and height are valid numbers
            length = float(obj.length)
            breadth = float(obj.breadth)
            height = float(obj.height)

            # Calculate volume weight
            volume_weight = (length * breadth * height) / 6000  # Division factor can be adjusted
            return round(volume_weight, 2)  # Return rounded value
        except (ValueError, TypeError):
            return None  # Return None if calculation fails
       

  
        


        



class OrderModelSerilizer(serializers.ModelSerializer):
    manage_staff = serializers.CharField(source="manage_staff.name")
    family = serializers.CharField(source="family.name")
    bank  = BankSerializer(read_only=True)
    billing_address = ShippingAddressView(read_only=True)
    customer = CustomerSerilizers(read_only=True)
    payment_receipts =  PaymentRecieptsViewSerializers(many=True,read_only=True)
    customerID = serializers.IntegerField(source="customer.pk")
    warehouse_orders=WarehousedataSerializer(many=True,read_only=True)


    class Meta:
        model = Order
        fields = ["id","manage_staff","updated_at","company","customer","invoice","billing_address","shipping_mode","code_charge","order_date","family","state","payment_status","status","total_amount","bank","payment_method","payment_receipts","shipping_charge","customerID","warehouse_orders"]


class LedgerSerializers(serializers.ModelSerializer):
    payment_receipts =  PaymentRecieptsViewSerializers(many=True,read_only=True)
    class Meta :
        model = Order
        fields = ["id","invoice","company","total_amount","order_date","payment_receipts"]

        
class OrderItemModelSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    actual_price = serializers.SerializerMethodField()
    exclude_price = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "name",
            "order",
            "product",
            "variant",
            "size",
            "description",
            "rate",
            "tax",
            "discount",
            "quantity",
            "actual_price",
            "exclude_price",
            "images"
        ]
        
        
    def get_name(self, obj):
        # Check if the product is a single or variant type
        if obj.product.type == "single":
            return obj.product.name
        elif obj.variant:
            return obj.variant.name
        return None
    
    def get_actual_price(self, obj):
        # Calculate the actual price based on the product type
        return int(obj.product.selling_price) if obj.product.selling_price is not None else None
    
    def get_exclude_price(self, obj):
        return int(obj.product.exclude_price) if obj.product.exclude_price is not None else None
    

    def get_images(self, obj):
        # Return a list of images based on the product type
        image_urls = []

        if obj.product.type == "single":
            # Fetch all images from the SingleProducts model for this product
            single_images = SingleProducts.objects.filter(product=obj.product)
            image_urls = [single_image.image.url for single_image in single_images if single_image.image]

        elif obj.variant:
            # Fetch all images from the VariantImages model for this variant
            variant_images = VariantImages.objects.filter(variant_product=obj.variant)
            image_urls = [variant_image.image.url for variant_image in variant_images if variant_image.image]

        return image_urls if image_urls else None



class AttributesModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attributes
        exclude = ['created_user']




class ProductAttributeModelSerilizer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = '__all__'
        
        
        
class BepocartSerializers(serializers.ModelSerializer):
    class Meta :
        model = BeposoftCart
        fields = "__all__"
        
        
        
class BepocartSerializersView(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()
    exclude_price = serializers.SerializerMethodField()

    class Meta:
        model = BeposoftCart
        fields = [
            "id",
            "product",
            "variant",
            "size",
            "discount",
            "quantity",
            "created_at",
            "name",
            "images",
            "price",
            "note",
            "tax",
            "rate",
            "exclude_price"
        ]

    def get_name(self, obj):
        # Check if the product is a single or variant type
        if obj.product.type == "single":
            return obj.product.name
        elif obj.variant:
            return obj.variant.name
        return None
    
    def get_exclude_price(self,obj):
        return int(obj.product.exclude_price) if obj.product.exclude_price is not None else None
    
    
    def get_tax(self,obj):
        return obj.product.tax
    
    def get_rate(self,obj):
        return obj.product.purchase_rate
        
        

    def get_images(self, obj):
        # Return a list of images based on the product type
        image_urls = []
        
        if obj.product.type == "single":
            # Fetch all images from the SingleProducts model for this product
            single_images = SingleProducts.objects.filter(product=obj.product)
            image_urls = [single_image.image.url for single_image in single_images if single_image.image]
        
        elif obj.variant:
            # Fetch all images from the VariantImages model for this variant
            variant_images = VariantImages.objects.filter(variant_product=obj.variant)
            image_urls = [variant_image.image.url for variant_image in variant_images if variant_image.image]

        return image_urls if image_urls else None


    def get_price(self, obj):
        # Get the price based on the product type
        if obj.product.type == "single":
            return obj.product.selling_price
        elif obj.variant :
            # Assuming variant price should be handled separately if needed
            return obj.product.selling_price  # or use a different field for variant price
        return None

    def get_size(self, obj):
        # Return the size name if the variant has a size
        if obj.variant and obj.variant.is_variant:
            return obj.size.attribute if obj.size else None
        return None



class PaymentRecieptSerializers(serializers.ModelSerializer):
    class Meta :
        model = PaymentReceipt
        fields = '__all__'




class PerfomaInvoiceOrderSerializers(serializers.ModelSerializer):
    class Meta :
        model = PerfomaInvoiceOrder
        fields = '__all__'
        
class PerfomaInvoiceProducts(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    actual_price = serializers.SerializerMethodField()
    exclude_price = serializers.SerializerMethodField()
    
    class Meta:
        model = PerfomaInvoiceOrderItem
        fields = [
            "id",
            "name",
            "order",
            "product",
            "variant",
            "size",
            "description",
            "rate",
            "tax",
            "discount",
            "quantity",
            "actual_price",
            "exclude_price",
            "images"
        ]
        
        
    def get_name(self, obj):
        # Check if the product is a single or variant type
        if obj.product.type == "single":
            return obj.product.name
        elif obj.variant:
            return obj.variant.name
        return None
    
    def get_actual_price(self, obj):
        # Calculate the actual price based on the product type
        return int(obj.product.selling_price) if obj.product.selling_price is not None else None
    
    def get_exclude_price(self, obj):
        return int(obj.product.exclude_price) if obj.product.exclude_price is not None else None
    

    def get_images(self, obj):
        # Return a list of images based on the product type
        image_urls = []

        if obj.product.type == "single":
            # Fetch all images from the SingleProducts model for this product
            single_images = SingleProducts.objects.filter(product=obj.product)
            image_urls = [single_image.image.url for single_image in single_images if single_image.image]

        elif obj.variant:
            # Fetch all images from the VariantImages model for this variant
            variant_images = VariantImages.objects.filter(variant_product=obj.variant)
            image_urls = [variant_image.image.url for variant_image in variant_images if variant_image.image]

        return image_urls if image_urls else None
        
class PerfomaInvoiceProductsSerializers(serializers.ModelSerializer):
    manage_staff = serializers.CharField(source="manage_staff.name")
    family = serializers.CharField(source="family.name")
    bank  = BankSerializer(read_only=True)
    billing_address = ShippingAddressView(read_only=True)
    customer = CustomerSerilizers(read_only=True)
    payment_receipts =  PaymentRecieptsViewSerializers(many=True,read_only=True)
    customerID = serializers.IntegerField(source="customer.pk")
    perfoma_items = PerfomaInvoiceProducts(many=True,read_only=True)
    class Meta:
        model = PerfomaInvoiceOrder
        fields = ["id","manage_staff","company","customer",
                  "invoice","billing_address",
                  "shipping_mode","code_charge","order_date","family",
                  "state","payment_status","status","total_amount",
                  "bank","payment_method","payment_receipts",
                  "shipping_charge","customerID","perfoma_items"]
        

class GRVSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source="order.customer.name")
    staff=serializers.CharField(source='order.manage_staff.name')
    invoice = serializers.CharField(source = "order.invoice")
    order_date = serializers.CharField(source="order.order_date")
    class Meta:
        model=GRVModel
        fields=['order','id','product','returnreason','price','quantity','remark','note','status','customer','invoice','staff',"order_date",'date','time','updated_at']
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'time' in representation and representation['time']:
            try:
                # Convert stored time into 12-hour format for the response
                time_obj = datetime.strptime(representation['time'], '%H:%M:%S')  # Assuming HH:MM:SS storage format
                representation['time'] = time_obj.strftime('%I:%M %p')  # Convert to hh:mm AM/PM
            except ValueError:
                pass  # Leave the time as-is if parsing fails
        return representation  
        # Customize the output format of the `time` field
           

class GRVModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GRVModel
        fields ='__all__'



class OrderUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseModel
        fields = "__all__"


class CompanySerializers(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"