from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Address
from .models import Order, OrderItem, Payment
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem, Cart
import datetime
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import Order, OrderItem, Payment
from django.utils import timezone
from .utils import get_cart_items
from .models import Coupon
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy
from collections import defaultdict
def user_required(user):
    return not user.is_staff and not user.is_superuser

user_login_required = user_passes_test(user_required, login_url=reverse_lazy('login'))

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()


        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')

@login_required
@user_login_required
def orders_address(request):
    user_addresses = Address.objects.filter(user=request.user).order_by('-id')  # Fetch all addresses and order by most recent
    if request.method == "POST":
        # Retrieve form data
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        address_line2 = request.POST.get('address_line2', '')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        # Create and save the address to the database
        Address.objects.create(
            user=request.user,
            full_name=full_name,
            address=address,
            address_line2=address_line2,
            city=city,
            state=state,
            pincode=pincode,
            phone=phone,
            email=email,    
            checked=True

        )

        # Success message and redirect
        messages.success(request, 'Address added successfully!')
        return redirect('checkout')  # Replace with the name of the view you want to redirect to
    
    return render(request, 'store/checkout.html', {'user_addresses': user_addresses})




@login_required
def update_address(request):
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address.full_name = request.POST.get('full_name')
        address.address = request.POST.get('address')
        address.address_line2 = request.POST.get('address_line2')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.pincode = request.POST.get('pincode')
        address.phone = request.POST.get('phone')
        address.email = request.POST.get('email')
        address.save()

        # Optionally, add a success message
        messages.success(request, 'Address updated successfully.')

    return redirect('checkout')  # Redirect to checkout page or wherever you need




def delete_address(request, id):
    # Get the address object or return a 404 error if not found
    address = get_object_or_404(Address, id=id)
    
    # Check if the request method is POST
    if request.method == 'POST':
        # Delete the address
        address.delete()
        
        # Add a success message
        messages.success(request, 'Address deleted successfully.')
        
        # Redirect to a desired page, for example, the address list page
        return redirect('checkout')  # Change 'address_list' to your actual view name

    # If the request method is not POST, redirect back to the address list
    return redirect('checkout')

def calculate_tax(total):
    # Implement tax calculation logic
    return total * 0.1  # Example tax rate of 10%


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from carts.models import CartItem, Cart
from carts.views import _cart_id
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import random
from carts.models import CheckoutDetails
from decimal import Decimal
from .models import Wallet, WalletTransaction
from django.db import transaction
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from .models import OrderedItems
@csrf_exempt
@login_required(login_url='login')
def place_order(request):
    if request.method == 'POST':
      
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        total = sum(item.sub_total() for item in cart_items)
        tax = (2 * total) / 100
        shipping_fee = 50
        grand_total = total + tax + shipping_fee
        payment_method = request.POST.get('payment_method')
        

      
        if payment_method == 'cash_on_delivery':
            # Handle Cash on Delivery
            checkoutdetails = CheckoutDetails.objects.filter(user=request.user).last()

            gt=checkoutdetails.grand_total
            if gt > 1000:
                messages.error(request, 'Orders above Rs 1000 cannot be placed with Cash on Delivery.')
                return redirect('checkout')  # Redirect to the checkout page or appropriate page
            order = Order(
                user=request.user,
                name=request.user.get_full_name(),
                email=request.user.email,
                total_price=total,
                tax=tax,
                grand_total=gt,
                payment_method=payment_method,
                status='Pending',
                shipping_fee = 50
            )
            coupon_deduction = checkoutdetails.before_price - order.grand_total
    
            order.coupon_price = coupon_deduction

            order.order_number = order.generate_unique_order_number()

            with transaction.atomic():
                order.save()

                # Create order items and update product stock
                # Dictionary to hold stock adjustments for each product
                stock_adjustments = defaultdict(lambda: {'small': 0, 'medium': 0, 'large': 0})

                for item in cart_items:
                    # Create ordered items
                    OrderedItems.objects.create(
                        product=item.product,
                        unit_price=item.unit_price,
                        quantity=item.quantity,
                        size=item.size,
                        order_number=order.order_number,
                        shipping_fee=order.shipping_fee
                    )
                    
                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        sub_total=item.sub_total(),
                    )
                    
                    # Adjust stock for this product based on size
                    if item.size == 'Size 3':
                        stock_adjustments[item.product]['small'] += item.quantity
                    elif item.size == 'Size 4':
                        stock_adjustments[item.product]['medium'] += item.quantity
                    elif item.size == 'Size 5':
                        stock_adjustments[item.product]['large'] += item.quantity

                # Update stock for each product only once
                for product, adjustments in stock_adjustments.items():
                    product.stock_small -= adjustments['small']
                    product.stock_medium -= adjustments['medium']
                    product.stock_large -= adjustments['large']
                    product.save()

                # No Payment entry needed for Cash on Delivery
                cart_items.delete()

            messages.success(request, 'Your order has been placed successfully!')
            return redirect('order_successful')  # Ensure this path is correct

        elif payment_method == 'wallet':
            # Handle Wallet Payment
            checkoutdetails = CheckoutDetails.objects.filter(user=request.user).last()
            gt = checkoutdetails.grand_total
            order = Order(
                user=request.user,
                name=request.user.get_full_name(),
                email=request.user.email,
                total_price=total,
                tax=tax,
                grand_total=gt,
                payment_method=payment_method,
                status='Pending',
                shipping_fee=50
            )
            coupon_deduction = checkoutdetails.before_price - order.grand_total
          
            order.coupon_price = coupon_deduction
            order.order_number = order.generate_unique_order_number()

            # Get user's wallet
            wallet = Wallet.objects.get(user=request.user)

            # Check if the wallet balance is sufficient
            if wallet.wallet_balance < gt:
                messages.error(request, 'Insufficient wallet balance.')
                return redirect('checkout')  # Redirect to the checkout page or another appropriate page
            
            with transaction.atomic():
                # Save order
                order.save()

                # Create order items and update product stock
                # Dictionary to hold stock adjustments for each product
                stock_adjustments = defaultdict(lambda: {'small': 0, 'medium': 0, 'large': 0})

                for item in cart_items:
                    # Create ordered items
                    OrderedItems.objects.create(
                        product=item.product,
                        unit_price=item.unit_price,
                        quantity=item.quantity,
                        size=item.size,
                        order_number=order.order_number,
                        shipping_fee=order.shipping_fee
                    )
                    
                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        sub_total=item.sub_total(),
                    )
                    
                    # Adjust stock for this product based on size
                    if item.size == 'Size 3':
                        stock_adjustments[item.product]['small'] += item.quantity
                    elif item.size == 'Size 4':
                        stock_adjustments[item.product]['medium'] += item.quantity
                    elif item.size == 'Size 5':
                        stock_adjustments[item.product]['large'] += item.quantity

                # Update stock for each product only once
                for product, adjustments in stock_adjustments.items():
                    product.stock_small -= adjustments['small']
                    product.stock_medium -= adjustments['medium']
                    product.stock_large -= adjustments['large']
                    product.save()

                # for item in cart_items:
                #     OrderedItems.objects.create(
                #         product=item.product,
                #         unit_price=item.unit_price,
                #         quantity=item.quantity,
                #         size=item.size,
                #         order_number=order.order_number,
                #         shipping_fee=order.shipping_fee
                #     )
                #     OrderItem.objects.create(
                #         order=order,
                #         product=item.product,
                #         quantity=item.quantity,
                #         sub_total=item.sub_total(),
                #     )

                #     # Reduce stock based on item size
                #     product = item.product
                #     if item.size == 'Size 3':
                #         product.stock_small -= item.quantity
                #     elif item.size == 'Size 4':
                #         product.stock_medium -= item.quantity
                #     elif item.size == 'Size 5':
                #         product.stock_large -= item.quantity

                #     product.save()

                # Create payment record
                Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount_paid=gt,  # Use grand_total as the amount paid
                )

                # Update wallet balance
                wallet.update_balance(transaction_type='debit', amount=gt)

                # Create wallet transaction record
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=gt,
                    transaction_type='debit',
                    description=f'Order #{order.order_number}',
                )

                # Clear cart items
                cart_items.delete()

            messages.success(request, 'Your order has been placed successfully!')
            return redirect('order_successful')  # Ensure this path is correct


        else:
           
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_signature = request.POST.get('razorpay_signature')

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            checkoutdetails = CheckoutDetails.objects.filter(user=request.user).last()
            gt = checkoutdetails.grand_total
            # order = Order(
            #     user=request.user,
            #     name=request.user.get_full_name(),
            #     email=request.user.email,
            #     total_price=total,
            #     tax=tax,
            #     grand_total=gt,
            #     payment_method=payment_method,
            #     status='Pending',
            # )
            try:
                # Verify payment signature
                client.utility.verify_payment_signature(params_dict)
                payment_status = "success"
            except razorpay.errors.SignatureVerificationError as e:
                payment_status = "failure"
                messages.error(request, 'Razorpay payment failed. Please try again.')
                return redirect('checkout')

            if payment_status == "success":
                # Proceed with order creation
                order = Order(
                    user=request.user,
                    name=request.user.get_full_name(),
                    email=request.user.email,
                    total_price=total,
                    tax=tax,
                    grand_total=gt,
                    payment_method='Razor Pay',
                    status='Pending',
                    shipping_fee=50
                )
                coupon_deduction = checkoutdetails.before_price - order.grand_total
              
                order.coupon_price = coupon_deduction
                order.order_number = order.generate_unique_order_number()

                with transaction.atomic():
                    order.save()

                    # Create order items and update product stock
                # Dictionary to hold stock adjustments for each product
                stock_adjustments = defaultdict(lambda: {'small': 0, 'medium': 0, 'large': 0})

                for item in cart_items:
                    # Create ordered items
                    OrderedItems.objects.create(
                        product=item.product,
                        unit_price=item.unit_price,
                        quantity=item.quantity,
                        size=item.size,
                        order_number=order.order_number,
                        shipping_fee=order.shipping_fee
                    )
                    
                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        sub_total=item.sub_total(),
                    )
                    
                    # Adjust stock for this product based on size
                    if item.size == 'Size 3':
                        stock_adjustments[item.product]['small'] += item.quantity
                    elif item.size == 'Size 4':
                        stock_adjustments[item.product]['medium'] += item.quantity
                    elif item.size == 'Size 5':
                        stock_adjustments[item.product]['large'] += item.quantity

                # Update stock for each product only once
                for product, adjustments in stock_adjustments.items():
                    product.stock_small -= adjustments['small']
                    product.stock_medium -= adjustments['medium']
                    product.stock_large -= adjustments['large']
                    product.save()

                    Payment.objects.create(
                        order=order,
                        payment_method=payment_method,
                        amount_paid=grand_total,
                    )

                    cart_items.delete()

                messages.success(request, 'Your order has been placed successfully!')
                return redirect('order_successful')  # Ensure this path is correct
    else:
        return redirect('cart')
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment, Order  # Import your Payment and Order models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from .models import Payment, Order

@csrf_protect
def process_payment(request):
    if request.method == 'POST':
        # Get payment details from POST request
        
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        order_id = request.POST.get('order_id')

        try:
            order = Order.objects.get(id=order_id)

            payment = Payment(
                order=order,
                payment_method='Razorpay',
                payment_status='Completed',
                amount_paid=order.total_amount,
                razorpay_payment_id=razorpay_payment_id,
                razorpay_order_id=razorpay_order_id,
                razorpay_signature=razorpay_signature
            )
            payment.save()

            return JsonResponse({'status': 'success', 'message': 'Payment processed successfully.'})

        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found.'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)





@login_required
def order_successful(request):
    return render(request, 'orders/order_successful.html')




def create_coupon(request):
    if request.method == "POST":
        code = request.POST.get('code')
        description = request.POST.get('description')
        discount_percentage = request.POST.get('discountPercentage')
        min_purchase_amount = request.POST.get('minPurchaseAmount')
        quantity = request.POST.get('quantity')
        expiry_date = request.POST.get('expiryDate')

        # Create a new Coupon instance and save it to the database
        coupon = Coupon(
            code=code,
            description=description,
            discount_percentage=discount_percentage,
            minimum_purchase_amount=min_purchase_amount,
            quantity=quantity,
            expiry_date=expiry_date,
            status='active',
        )
        coupon.save()

        messages.success(request, 'Coupon created successfully!')
        return redirect('admincoupons')


    return render(request, 'admins/coupons.html')


def toggle_coupon_status(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if coupon.action == 'block':
        coupon.status = 'inactive'
        coupon.action = 'unblock'
    else:
        coupon.status = 'active'
        coupon.action = 'block'
    coupon.save()
    return redirect('admincoupons')  # Redirect to the view that lists all coupons
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Coupon
from carts.models import CheckoutDetails

logger = logging.getLogger(__name__)

@csrf_exempt
def apply_coupon(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            coupon_code = data.get('coupon_code')
            
            coupon = get_object_or_404(Coupon, code=coupon_code, status='active')
            
            if coupon.expiry_date < timezone.now().date():
                return JsonResponse({'success': False, 'message': "This coupon has expired."})
            
            order = CheckoutDetails.objects.filter(user=request.user).last()
            
            if not order:
                return JsonResponse({'success': False, 'message': "No active order found."})
            
            if order.grand_total < coupon.minimum_purchase_amount:
                return JsonResponse({'success': False, 'message': f"Order amount does not meet the minimum purchase amount of ₹{coupon.minimum_purchase_amount} for this coupon."})
            
            discount_amount = (coupon.discount_percentage / 100) * order.grand_total
            
            order.grand_total -= discount_amount
            order.coupon = coupon
            order.coupon_applied = True
            order.save()
            
            logger.info(f"Coupon {coupon_code} applied successfully to order {order.id}. Coupon ID: {coupon.id}")
            logger.info(f"Order details after applying coupon: Grand Total: {order.grand_total}, Coupon Applied: {order.coupon_applied}, Coupon ID: {order.coupon_id}")
            
            return JsonResponse({'success': True, 'new_grand_total': round(order.grand_total, 2)})
        
        except Coupon.DoesNotExist:
            logger.warning(f"Invalid coupon code attempted: {coupon_code}")
            return JsonResponse({'success': False, 'message': "Invalid coupon code."})
        except Exception as e:
            logger.error(f"Error in apply_coupon: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'message': "Invalid coupon"})
    
    return JsonResponse({'success': False, 'message': "Invalid request."})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from carts.models import CheckoutDetails
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def remove_coupon(request):
    if request.method == 'POST':
        try:
            # Retrieve the active order (CheckoutDetails) for the current user where a coupon was applied
            order = CheckoutDetails.objects.filter(user=request.user, coupon_applied=True).last()
            
            if not order:
                return JsonResponse({'success': False, 'message': "No coupon applied or no active order found."})
            
            if order.coupon is None:
                logger.error(f"Coupon is None for order {order.id}")
                return JsonResponse({'success': False, 'message': "Coupon information is missing."})
            
            # Calculate the original grand total (before discount)
            discount_percentage = order.coupon.discount_percentage
            original_grand_total = order.grand_total / (1 - (discount_percentage / 100))
            
            # Update the order
            order.grand_total = original_grand_total
            order.coupon_applied = False
            order.coupon = None  # Remove the coupon relationship
            order.save()
            
            logger.info(f"Coupon removed successfully for order {order.id}")
            return JsonResponse({'success': True, 'new_grand_total': round(order.grand_total, 2)})
        
        except Exception as e:
            logger.error(f"Error in remove_coupon: {str(e)}")
            return JsonResponse({'success': False, 'message': "An error occurred while removing the coupon."})
    
    return JsonResponse({'success': False, 'message': "Invalid request."})
