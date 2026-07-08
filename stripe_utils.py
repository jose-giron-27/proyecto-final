# stripe_utils.py - Integración de Stripe para AutoMenu AI (Fase 12 - Demo)
# -----------------------------------------------------------------------------
# Este módulo maneja la simulación de pagos con Stripe en modo TEST/SANDBOX.
# No se realiza ningún cobro real: usamos tarjetas de prueba de Stripe
# (ej. 4242 4242 4242 4242) únicamente para fines de demostración.
#
# Flujo general:
#   1. El usuario hace click en "Actualizar a Pro" -> POST /subscribe
#   2. crear_checkout_session() crea una sesión de pago en Stripe y devuelve
#      una URL a la que redirigimos al usuario (Stripe Checkout, hosteado
#      por Stripe, no construimos ningún formulario de tarjeta nosotros).
#   3. Stripe redirige de vuelta a /subscription/success?session_id=...
#   4. verificar_pago() confirma con Stripe que el pago sí se completó
#      (nunca confiamos ciegamente en el redirect) y ahí marcamos el
#      restaurante como "pro" en la base de datos.
# -----------------------------------------------------------------------------

import os
import stripe

# La Secret Key nunca se hardcodea: siempre se lee desde variables de entorno (.env)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# ID del precio (Price ID) del Plan Pro, creado previamente en el Dashboard
# de Stripe: Producto "AutoMenu AI - Plan Pro", GTQ 249.99 / mes recurrente.
STRIPE_PRICE_ID_PRO = os.environ.get("STRIPE_PRICE_ID_PRO")


# ─── Crear sesión de Checkout ──────────────────────────────────────────────
def crear_checkout_session(restaurant_id, success_url, cancel_url, email=None):
    """
    Crea una sesión de Stripe Checkout para suscribirse al Plan Pro.

    Parámetros:
        restaurant_id (str): id del restaurante que se está suscribiendo.
                              Se guarda en metadata para poder identificarlo
                              cuando Stripe confirme el pago.
        success_url (str): URL a la que Stripe redirige si el pago fue exitoso.
                            Debe incluir el placeholder {CHECKOUT_SESSION_ID}.
        cancel_url (str): URL a la que Stripe redirige si el usuario cancela.
        email (str, opcional): email del usuario, para prellenar el checkout.

    Retorna:
        dict: {"ok": True, "url": "..."} o {"ok": False, "error": "..."}
    """
    try:
        if not STRIPE_PRICE_ID_PRO:
            return {"ok": False, "error": "STRIPE_PRICE_ID_PRO no está configurado en .env"}

        sesion = stripe.checkout.Session.create(
            mode="subscription",  # Suscripción recurrente (no pago único)
            line_items=[{
                "price": STRIPE_PRICE_ID_PRO,
                "quantity": 1,
            }],
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=email,
            # Guardamos el restaurant_id para poder actualizar el plan
            # correcto cuando confirmemos el pago en /subscription/success
            metadata={"restaurant_id": restaurant_id},
        )

        return {"ok": True, "url": sesion.url}

    except Exception as e:
        print(f"[stripe_utils] Error en crear_checkout_session: {e}")
        return {"ok": False, "error": str(e)}


# ─── Verificar pago ─────────────────────────────────────────────────────────
def verificar_pago(session_id):
    """
    Verifica directamente con Stripe (no con el navegador del usuario) que
    una sesión de checkout realmente se pagó, antes de activar el Plan Pro.

    Parámetros:
        session_id (str): el ID de sesión que Stripe manda como query param
                           (?session_id=...) al redirigir a success_url.

    Retorna:
        dict: {"ok": True, "pagado": bool, "restaurant_id": str}
              o {"ok": False, "error": "..."}
    """
    try:
        sesion = stripe.checkout.Session.retrieve(session_id)

        pagado = sesion.payment_status == "paid"
        restaurant_id = sesion.metadata.get("restaurant_id")

        return {"ok": True, "pagado": pagado, "restaurant_id": restaurant_id}

    except Exception as e:
        print(f"[stripe_utils] Error en verificar_pago: {e}")
        return {"ok": False, "error": str(e)}
