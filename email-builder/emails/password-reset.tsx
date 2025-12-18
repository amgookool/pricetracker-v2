import { Body, Button, Column, Container, Head, Html, Img, Link, Preview, Row, Section, Tailwind, TailwindProps, Text } from '@react-email/components';

interface ResetPasswordEmailProps {
	resetLink?: string;
	name?: string;
}

const tailwindConfig: TailwindProps['config'] = {
      theme: {
        extend: {
          colors: {},
        },
      },
};

export const ResetPasswordEmail = ({ resetLink, name }: ResetPasswordEmailProps) => (
 <Html>
      <Head />
      <Tailwind config={tailwindConfig}>
        <Body className="bg-[#efeef1] font-twitch">
          <Preview>PricePulse - Reset Your Password</Preview>
          <Container className="max-w-145 mx-auto bg-white">
            <Section className="py-4">
              <Img
                width={114}
                src={`/static/price-pulse.svg`}
                alt="PricePulse"
                className="mx-auto"
              />
            </Section>
            <Section className="w-full">
              <Row>
                <Column className="[border-bottom:1px_solid_rgb(238,238,238)] w-62.25" />
                <Column className="[border-bottom:1px_solid_rgb(0,122,206)] w-48" />
                <Column className="[border-bottom:1px_solid_rgb(238,238,238)] w-62.25" />
              </Row>
            </Section>
            <Section className="pt-1.25 px-5 pb-2.5">
              <Text className="text-[14px] leading-normal">Hi {'{{ name }}'},</Text>
              <Text className="text-[14px] leading-normal">
                We received a request to reset the password for your account associated with this email address.
                
              </Text>
              <Text className="text-[14px] leading-normal">
                To reset your password, please click the button below:
              </Text>
              <Section className="text-center my-6">
                <Button
                    href='{{ resetLink }}'
                    className="bg-[#007ACC] text-white text-[16px] font-semibold py-2.5 px-6 rounded-md"
                >
                    Reset Password
                </Button>
              </Section>
              <Text className=''>
                If the button above does not work, please copy and paste the following link into your web browser:
                <Link href='{{ resetLink }}' className="break-all text-[#007ACC]">{'{{ resetLink }}'}</Link>
              </Text>
              <Text className="text-[14px] leading-normal">
                If you did not request a password reset, please ignore this email. Your password will remain unchanged.
              </Text>
            </Section>
          </Container>
        </Body>
      </Tailwind>
    </Html>
);

export default ResetPasswordEmail;
