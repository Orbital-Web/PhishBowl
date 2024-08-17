// Modify this to add more endpoints
const routeEndpoints = {
  home: "/",
  emailAnalysis: "/analyze/email/",
  imageAnalysis: "/analyze/image/",
  result: "/result/",
};
type routes = keyof typeof routeEndpoints;

export default function getRoutes(
  route: routes,
  queryParams: Record<string, any> = {}
): string {
  let endpoint = routeEndpoints[route];

  // apply query params
  if (queryParams) {
    const queryString = new URLSearchParams(queryParams).toString();
    endpoint += `?${queryString}`;
  }

  return endpoint;
}
