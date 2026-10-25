INSERT INTO users (id, email, name) VALUES
    ('11111111-1111-1111-1111-111111111111', 'alice@example.com', 'Alice'),
    ('22222222-2222-2222-2222-222222222222', 'bob@example.com', 'Bob')
ON CONFLICT (id) DO NOTHING;

INSERT INTO products (id, name, price, currency, stock_quantity) VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Blue Kettle', 45.00, 'USD', 10),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'Wool Blanket', 89.99, 'USD', 5),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'Ceramic Mug', 12.50, 'USD', 100)
ON CONFLICT (id) DO NOTHING;

INSERT INTO carts (id, user_id, status) VALUES
    (
        'c1c1c1c1-c1c1-c1c1-c1c1-c1c1c1c1c1c1',
        '11111111-1111-1111-1111-111111111111',
        'active'
    )
ON CONFLICT (id) DO NOTHING;

INSERT INTO cart_items (cart_id, product_id, quantity, unit_price)
SELECT
    v.cart_id,
    v.product_id,
    v.quantity,
    v.unit_price
FROM (
    VALUES
    (
        'c1c1c1c1-c1c1-c1c1-c1c1-c1c1c1c1c1c1'::uuid,
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
        1,
        45.00::numeric
    ),
    (
        'c1c1c1c1-c1c1-c1c1-c1c1-c1c1c1c1c1c1'::uuid,
        'cccccccc-cccc-cccc-cccc-cccccccccccc'::uuid,
        2,
        12.50::numeric
    )
) AS v (cart_id, product_id, quantity, unit_price)
WHERE NOT EXISTS (
    SELECT 1
    FROM cart_items AS existing
    WHERE existing.cart_id = v.cart_id
      AND existing.product_id = v.product_id
);

INSERT INTO user_payment_methods (
    id,
    user_id,
    provider_token,
    last_four,
    is_default
) VALUES
(
    '11111111-2222-3333-4444-555555555555',
    '11111111-1111-1111-1111-111111111111',
    'tok_test_alice_visa',
    '4242',
    TRUE
)
ON CONFLICT (id) DO NOTHING;
