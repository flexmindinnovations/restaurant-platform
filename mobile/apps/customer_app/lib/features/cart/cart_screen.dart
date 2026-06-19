import 'package:customer_app/features/cart/cart_provider.dart';
import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class CartScreen extends ConsumerStatefulWidget {
  const CartScreen({super.key});

  @override
  ConsumerState<CartScreen> createState() => _CartScreenState();
}

class _CartScreenState extends ConsumerState<CartScreen> {
  final _formKey = GlobalKey<FormState>();
  final _streetController = TextEditingController(text: '123 Tech Lane');
  final _cityController = TextEditingController(text: 'Metro City');
  final _stateController = TextEditingController(text: 'CA');
  final _postalCodeController = TextEditingController(text: '94043');
  final _countryController = TextEditingController(text: 'USA');
  final _notesController = TextEditingController();
  final _couponController = TextEditingController();
  String _appliedPromo = '';

  double _tipAmount = 2;
  String _paymentMethod = 'Credit Card';
  bool _isCheckingOut = false;

  @override
  void dispose() {
    _streetController.dispose();
    _cityController.dispose();
    _stateController.dispose();
    _postalCodeController.dispose();
    _countryController.dispose();
    _notesController.dispose();
    _couponController.dispose();
    super.dispose();
  }

  Future<void> _checkout() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isCheckingOut = true;
    });

    try {
      final orderId = await ref
          .read(cartProvider.notifier)
          .placeOrder(
            street: _streetController.text.trim(),
            city: _cityController.text.trim(),
            stateName: _stateController.text.trim(),
            postalCode: _postalCodeController.text.trim(),
            country: _countryController.text.trim(),
            tip: _tipAmount,
            notes: _notesController.text.trim(),
          );

      if (mounted) {
        context.pushReplacement('/tracking/$orderId');
      }
    } on Exception catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Checkout failed: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isCheckingOut = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final cart = ref.watch(cartProvider);

    if (cart.items.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: const Text('Cart')),
        body: const Center(
          child: Text('Your cart is empty.'),
        ),
      );
    }

    return LoadingOverlay(
      isLoading: _isCheckingOut,
      child: Scaffold(
        appBar: AppBar(title: const Text('Checkout')),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Order Review',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 8),
                ...cart.items.map((item) {
                  return ListTile(
                    contentPadding: EdgeInsets.zero,
                    title: Text(item.name),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (item.specialInstructions != null)
                          Text(
                            item.specialInstructions!,
                            style: const TextStyle(
                              fontSize: 12,
                              fontStyle: FontStyle.italic,
                            ),
                          ),
                        Row(
                          children: [
                            IconButton(
                              icon: const Icon(
                                Icons.remove_circle_outline,
                                size: 20,
                              ),
                              onPressed: () => ref
                                  .read(cartProvider.notifier)
                                  .updateItemQuantity(
                                    item.menuItemId,
                                    item.quantity - 1,
                                  ),
                            ),
                            Text('${item.quantity}'),
                            IconButton(
                              icon: const Icon(
                                Icons.add_circle_outline,
                                size: 20,
                              ),
                              onPressed: () => ref
                                  .read(cartProvider.notifier)
                                  .updateItemQuantity(
                                    item.menuItemId,
                                    item.quantity + 1,
                                  ),
                            ),
                          ],
                        ),
                      ],
                    ),
                    trailing: Text(
                      '\$${item.subtotal.toStringAsFixed(2)}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  );
                }),
                const Divider(),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Subtotal', style: TextStyle(fontSize: 16)),
                    Text(
                      '\$${cart.totalAmount.toStringAsFixed(2)}',
                      style: const TextStyle(fontSize: 16),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Text(
                  'Delivery Address',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                AppTextField(
                  controller: _streetController,
                  labelText: 'Street',
                  validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: AppTextField(
                        controller: _cityController,
                        labelText: 'City',
                        validator: (v) =>
                            v == null || v.isEmpty ? 'Required' : null,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: AppTextField(
                        controller: _stateController,
                        labelText: 'State',
                        validator: (v) =>
                            v == null || v.isEmpty ? 'Required' : null,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: AppTextField(
                        controller: _postalCodeController,
                        labelText: 'Postal Code',
                        validator: (v) =>
                            v == null || v.isEmpty ? 'Required' : null,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: AppTextField(
                        controller: _countryController,
                        labelText: 'Country',
                        validator: (v) =>
                            v == null || v.isEmpty ? 'Required' : null,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Text(
                  'Delivery Options & Tip',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                AppTextField(
                  controller: _notesController,
                  labelText: 'Delivery Notes (e.g. Leave at door)',
                ),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Driver Tip', style: TextStyle(fontSize: 16)),
                    DropdownButton<double>(
                      value: _tipAmount,
                      onChanged: (val) {
                        if (val != null) {
                          setState(() {
                            _tipAmount = val;
                          });
                        }
                      },
                      items: [0.0, 2.0, 5.0, 10.0].map((t) {
                        return DropdownMenuItem(
                          value: t,
                          child: Text('\$${t.toStringAsFixed(2)}'),
                        );
                      }).toList(),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Text(
                  'Promo Code',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: AppTextField(
                        controller: _couponController,
                        labelText: 'Enter coupon/promo code',
                      ),
                    ),
                    const SizedBox(width: 8),
                    ElevatedButton(
                      onPressed: () {
                        setState(() {
                          _appliedPromo = _couponController.text.trim();
                           if (_appliedPromo.isNotEmpty) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text(
                                  'Promo code "$_appliedPromo" applied!',
                                ),
                              ),
                            );
                          }
                        });
                      },
                      child: const Text('Apply'),
                    ),
                  ],
                ),
                if (_appliedPromo.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text(
                    'Applied Promo: $_appliedPromo (10% discount applied)',
                    style: const TextStyle(
                      color: Colors.green,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
                const SizedBox(height: 16),
                Text(
                  'Payment Method',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                Row(
                  children: ['Credit Card', 'Cash on Delivery'].map((m) {
                    final isSelected = _paymentMethod == m;
                    return Expanded(
                      child: InkWell(
                        onTap: () {
                          setState(() {
                            _paymentMethod = m;
                          });
                        },
                        child: Container(
                          padding: const EdgeInsets.all(12),
                          margin: const EdgeInsets.symmetric(horizontal: 4),
                          decoration: BoxDecoration(
                            border: Border.all(
                              color: isSelected
                                  ? Theme.of(context).colorScheme.primary
                                  : Theme.of(context).dividerColor,
                              width: isSelected ? 2 : 1,
                            ),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Center(
                            child: Text(
                              m,
                              style: TextStyle(
                                fontWeight: isSelected
                                    ? FontWeight.bold
                                    : FontWeight.normal,
                              ),
                            ),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
                const Divider(),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Total Price',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      () {
                        final rate = _appliedPromo.isNotEmpty ? 0.90 : 1.0;
                        final total = cart.totalAmount * rate + _tipAmount;
                        return '\$${total.toStringAsFixed(2)}';
                      }(),
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                AppButton(
                  text: 'Place Order',
                  onPressed: _checkout,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
