"""Tests for HTTP status code constants."""
import pytest
from fasthttp import status


class TestInformationalCodes:
    def test_100_continue(self):
        assert status.HTTP_100_CONTINUE == 100

    def test_101_switching_protocols(self):
        assert status.HTTP_101_SWITCHING_PROTOCOLS == 101

    def test_102_processing(self):
        assert status.HTTP_102_PROCESSING == 102

    def test_103_early_hints(self):
        assert status.HTTP_103_EARLY_HINTS == 103


class TestSuccessCodes:
    def test_200_ok(self):
        assert status.HTTP_200_OK == 200

    def test_201_created(self):
        assert status.HTTP_201_CREATED == 201

    def test_202_accepted(self):
        assert status.HTTP_202_ACCEPTED == 202

    def test_204_no_content(self):
        assert status.HTTP_204_NO_CONTENT == 204

    def test_206_partial_content(self):
        assert status.HTTP_206_PARTIAL_CONTENT == 206


class TestRedirectCodes:
    def test_301_moved_permanently(self):
        assert status.HTTP_301_MOVED_PERMANENTLY == 301

    def test_302_found(self):
        assert status.HTTP_302_FOUND == 302

    def test_304_not_modified(self):
        assert status.HTTP_304_NOT_MODIFIED == 304

    def test_307_temporary_redirect(self):
        assert status.HTTP_307_TEMPORARY_REDIRECT == 307

    def test_308_permanent_redirect(self):
        assert status.HTTP_308_PERMANENT_REDIRECT == 308


class TestClientErrorCodes:
    def test_400_bad_request(self):
        assert status.HTTP_400_BAD_REQUEST == 400

    def test_401_unauthorized(self):
        assert status.HTTP_401_UNAUTHORIZED == 401

    def test_403_forbidden(self):
        assert status.HTTP_403_FORBIDDEN == 403

    def test_404_not_found(self):
        assert status.HTTP_404_NOT_FOUND == 404

    def test_405_method_not_allowed(self):
        assert status.HTTP_405_METHOD_NOT_ALLOWED == 405

    def test_408_request_timeout(self):
        assert status.HTTP_408_REQUEST_TIMEOUT == 408

    def test_409_conflict(self):
        assert status.HTTP_409_CONFLICT == 409

    def test_410_gone(self):
        assert status.HTTP_410_GONE == 410

    def test_418_im_a_teapot(self):
        assert status.HTTP_418_IM_A_TEAPOT == 418

    def test_422_unprocessable_content(self):
        assert status.HTTP_422_UNPROCESSABLE_CONTENT == 422

    def test_429_too_many_requests(self):
        assert status.HTTP_429_TOO_MANY_REQUESTS == 429


class TestServerErrorCodes:
    def test_500_internal_server_error(self):
        assert status.HTTP_500_INTERNAL_SERVER_ERROR == 500

    def test_501_not_implemented(self):
        assert status.HTTP_501_NOT_IMPLEMENTED == 501

    def test_502_bad_gateway(self):
        assert status.HTTP_502_BAD_GATEWAY == 502

    def test_503_service_unavailable(self):
        assert status.HTTP_503_SERVICE_UNAVAILABLE == 503

    def test_504_gateway_timeout(self):
        assert status.HTTP_504_GATEWAY_TIMEOUT == 504


class TestStatusCodeValues:
    def test_1xx_are_informational(self):
        codes_1xx = [
            status.HTTP_100_CONTINUE,
            status.HTTP_101_SWITCHING_PROTOCOLS,
            status.HTTP_102_PROCESSING,
            status.HTTP_103_EARLY_HINTS,
        ]
        assert all(100 <= c < 200 for c in codes_1xx)

    def test_2xx_are_success(self):
        codes_2xx = [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_202_ACCEPTED,
            status.HTTP_204_NO_CONTENT,
        ]
        assert all(200 <= c < 300 for c in codes_2xx)

    def test_3xx_are_redirect(self):
        codes_3xx = [
            status.HTTP_301_MOVED_PERMANENTLY,
            status.HTTP_302_FOUND,
            status.HTTP_307_TEMPORARY_REDIRECT,
        ]
        assert all(300 <= c < 400 for c in codes_3xx)

    def test_4xx_are_client_errors(self):
        codes_4xx = [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
        ]
        assert all(400 <= c < 500 for c in codes_4xx)

    def test_5xx_are_server_errors(self):
        codes_5xx = [
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.HTTP_502_BAD_GATEWAY,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        ]
        assert all(500 <= c < 600 for c in codes_5xx)

    def test_all_codes_are_integers(self):
        import fasthttp.status as s
        for name in s.__all__:
            val = getattr(s, name)
            assert isinstance(val, int), f"{name} is not int"

    def test_all_codes_unique(self):
        import fasthttp.status as s
        values = [getattr(s, name) for name in s.__all__]
        assert len(values) == len(set(values)), "Duplicate status codes found"

    def test_all_codes_in_valid_range(self):
        import fasthttp.status as s
        for name in s.__all__:
            val = getattr(s, name)
            assert 100 <= val < 600, f"{name}={val} out of range"
